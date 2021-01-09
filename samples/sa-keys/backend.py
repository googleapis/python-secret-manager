import base64
import json
import os
import re
import sys
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from http import HTTPStatus
from random import randrange

import google.api_core
import google.api_core.exceptions
import googleapiclient.discovery
import googleapiclient.discovery
import opencensus.trace.tracer
from flask import jsonify
from gcloud import pubsub  # used to get project ID
from google.cloud import error_reporting
from google.cloud import logging
from google.cloud import secretmanager
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter

MAX_WORKERS = os.getenv('MAX_THREADS', 20)
KEY_DELETED_SA = 'deleted'
KEY_SA_KEY_NAMES = 'names'
KEY_SA_KEY_DETAILS = 'keys'

#     DEFAULT = 0
#     DEBUG = 100
#     INFO = 200
#     NOTICE = 300
#     WARNING = 400
#     ERROR = 500
#     CRITICAL = 600
#     ALERT = 700
#     EMERGENCY = 800
LOG_SEVERITY_DEFAULT = 'DEFAULT'
LOG_SEVERITY_INFO = 'INFO'
LOG_SEVERITY_WARNING = 'WARNING'
LOG_SEVERITY_DEBUG = 'DEBUG'
LOG_SEVERITY_NOTICE = 'NOTICE'
LOG_SEVERITY_ERROR = 'ERROR'

SA_KEY_REGEX = 'projects/([\w-]+)/serviceAccounts/([\w@-]+)\.iam\.gserviceaccount\.com/keys/(\w+)$'
SA_REGEX = '^([\w-]+)@([\w-]+)\.iam\.gserviceaccount\.com$'
SECRET_REGEX = '^[\w-]+$'
app_name = 'sa-keys'


def initialize_tracer(project_id):
    exporter = stackdriver_exporter.StackdriverExporter(
        project_id=project_id
    )
    tracer = opencensus.trace.tracer.Tracer(
        exporter=exporter,
        sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
    )

    return tracer


pubsub_client = pubsub.Client()
gcp_log_trace_project_id = os.getenv('GCP_PROJECT', pubsub_client.project)

gcp_tracer = initialize_tracer(gcp_log_trace_project_id)
error_reporting_client = error_reporting.Client()


def log(text, severity=LOG_SEVERITY_DEFAULT, log_name=app_name):
    logging_client = logging.Client()
    logger = logging_client.logger(log_name)

    return logger.log_text(text, severity=severity,
                           resource=google.cloud.logging.Resource(type="cloud_run_revision",
                                                                  labels={
                                                                      'configuration_name': 'flask-backend'
                                                                  }))


def audit_secrets_sa(secret_manager_project_id, secret_regex):
    """ Find possibly all the secrets in the project by filtering secret names containing ${PROJECT_ID}_
    Args:
        secret_manager_project_id (str): Project ID of the secret manager
        secret_regex:  regular expression to match secret name
    Returns:
        execution result, severity level
    """
    sm_client = secretmanager.SecretManagerServiceClient()
    list_secrets = sm_client.list_secrets(request={'parent': f"projects/{secret_manager_project_id}"})
    list_secrets_SA = [s.name.split('/')[-1] for s in list_secrets if re.search(secret_regex, s.name.split('/')[-1])]

    return audit_secrets_sa_batch(secret_manager_project_id, list_secrets_SA)


def audit_secrets_sa_batch(secret_manager_project_id, secrets):
    if not isinstance(secrets, list):
        raise TypeError("Secrets argument as a list is expected but it is NOT!")

    thread_results = {}
    tracer = gcp_tracer
    with tracer.start_span(name=f"{app_name}:audit_secret_sa_batch()") as span_method:
        with ThreadPoolExecutor(max_workers=int(MAX_WORKERS)) as executor:
            for secret_name in secrets:
                key = f"projects/{secret_manager_project_id}/secrets/{secret_name}/ops/{randrange(sys.maxsize)}"
                thread_results[key] = executor.submit(audit_secret_sa,
                                                      secret_manager_project_id,
                                                      secret_name)
            futures.wait(thread_results.values(), return_when=futures.ALL_COMPLETED)

        for key in thread_results:
            # exception thrown from .result() method if any exception happened
            try:
                thread_results[key] = thread_results[key].result()
            except Exception as ex:
                error_reporting_client.report_exception()
                thread_results[key] = ex

    return thread_results


def audit_secret_sa(secret_manager_project_id, secret_name):
    """ Examine the secret content to see if a valid Google service account key exists. Log to Cloud logging
        of the audit results. Delete the secret if the service account in the latest version of the secret
        does not exist.
    Args:
            secret_manager_project_id (str): Project ID of the secret manager
            secret_name (str): name of the secret

    Returns:
            execution result, severity level
    """
    sm_client = secretmanager.SecretManagerServiceClient()
    log_name_audit = f"{app_name}-audit"
    secret_path_latest = sm_client.secret_path(secret_manager_project_id, secret_name) + "/versions/latest"

    # check if the secret exists
    secret_latest_ver = sm_client.access_secret_version(request={"name": secret_path_latest})
    secret_content = secret_latest_ver.payload.data.decode("UTF-8")

    try:
        secret_json = json.loads(secret_content)
        sa = secret_json['client_email']
        private_key_id = secret_json['private_key_id']
    except Exception as ex:
        warning = f"Failed to parse Service Account JSON key in secret payload: {ex}"
        log(warning, LOG_SEVERITY_WARNING, log_name=log_name_audit)
        return warning, LOG_SEVERITY_WARNING

    # find service account key id
    from googleapiclient.errors import HttpError
    try:
        keys = get_sa_keys_days_older(sa, 0)
    except HttpError as sa_not_found:
        # in case of SA in secret's latest version but can't be found (perhaps due to lack of access)
        warning = f"Secret {secret_path_latest} has a service account that does not exist: {sa_not_found};" \
                  f" recommend to delete the secret"
        log(warning, LOG_SEVERITY_WARNING, log_name=log_name_audit)
        return warning, LOG_SEVERITY_WARNING

    key_names = keys[KEY_SA_KEY_NAMES]
    discovered_sa_key_ids = []
    for name in key_names:
        regex_search_result = re.search(SA_KEY_REGEX, name)
        discovered_sa_key_ids.append(regex_search_result.group(3))

    if private_key_id in discovered_sa_key_ids:
        notice = f"Service account key in secret {secret_path_latest} exists for {sa}"
        log(notice, LOG_SEVERITY_NOTICE, log_name=log_name_audit)
        return notice, LOG_SEVERITY_NOTICE
    else:
        warning = f"Secret {secret_path_latest} has invalid service account key for {sa};" \
                  f" valid keys may exist in older versions"
        log(warning, LOG_SEVERITY_WARNING, log_name=log_name_audit)
        return warning, LOG_SEVERITY_WARNING


def put_secret(sa_key, secret_manager_project_id, secret_name):
    try:
        sm_client = secretmanager.SecretManagerServiceClient()
        secret_full_name = sm_client.secret_path(secret_manager_project_id, secret_name)

        # check if the secret exists
        find_secret_result_local = sm_client.get_secret(request={"name": secret_full_name})
    except google.api_core.exceptions.NotFound as secret_not_found:
        find_secret_result_local = None
        log(f"{app_name}:put_secret secret {secret_full_name} not found", severity=LOG_SEVERITY_DEBUG)
    # if the given secret not found, create the secret
    if not find_secret_result_local:
        parent = f"projects/{secret_manager_project_id}"
        create_secret_result_local = sm_client.create_secret(request={
            "parent": parent,
            "secret_id": secret_name,
            "secret": {"replication": {"automatic": {}}}
        })

        log(f"{app_name}:put_secret secret {create_secret_result_local.name} created",
            severity=LOG_SEVERITY_INFO)
    else:
        create_secret_result_local = None
    # update the secret version
    parent = sm_client.secret_path(secret_manager_project_id, secret_name)
    add_secret_ver_result_local = sm_client.add_secret_version(
        request={"parent": parent, "payload": {"data": sa_key}}
    )

    return find_secret_result_local, create_secret_result_local, add_secret_ver_result_local


def delete_sa_keys_base(full_sa_key_names):
    if not full_sa_key_names:
        log(f"{app_name}:delete_sa_keys_base has empty key names as input",
            severity=LOG_SEVERITY_WARNING)
        return {KEY_DELETED_SA: []}

    for full_sa_key_name in full_sa_key_names:
        regex_search_result = re.search(SA_KEY_REGEX, full_sa_key_name)
        if not regex_search_result or len(regex_search_result.groups()) != 3:
            raise ValueError(f"input parameter {full_sa_key_name} failed to match regular expression {SA_KEY_REGEX}")

    tracer = gcp_tracer
    with tracer.start_span(name=f"{app_name}:delete_sa_keys_base()") as span_method:
        keys_deleted = []

        for full_sa_key_name in full_sa_key_names:
            service = googleapiclient.discovery.build('iam', 'v1')
            full_sa_key_name = full_sa_key_name.strip()
            try:
                service.projects().serviceAccounts().keys().delete(name=full_sa_key_name).execute()
            except Exception as ex:
                error_reporting_client.report_exception()
                err_resp = {
                    'error': str(ex),
                    KEY_DELETED_SA: keys_deleted
                }
                if isinstance(ex, googleapiclient.errors.HttpError):
                    return err_resp, ex.resp.status
                elif isinstance(ex, google.api_core.exceptions.GoogleAPIError):
                    return err_resp, ex.code
                else:
                    return err_resp, HTTPStatus.INTERNAL_SERVER_ERROR

            keys_deleted.append(full_sa_key_name)

        log(f"{app_name}:delete_sa_keys_base deleted {keys_deleted}", severity=LOG_SEVERITY_INFO)
    return {KEY_DELETED_SA: keys_deleted}


def gen_key(service_account):
    service = googleapiclient.discovery.build('iam', 'v1')
    key = service.projects().serviceAccounts().keys().create(
        name='projects/-/serviceAccounts/' + service_account, body={
            'privateKeyType': 'TYPE_GOOGLE_CREDENTIALS_FILE'
        }).execute()
    sa_key = base64.b64decode(key['privateKeyData'])
    log(f"{app_name}:gen_key created service account key succeeded: {key['name']}",
        severity=LOG_SEVERITY_INFO)
    return sa_key


def get_sa_keys(sa):
    """Lists all keys for a service account.
    Args:
        sa (str): Google Service Account.

    Returns:
        keys of the Google Service Account:
        "keys": [
        {
            "keyAlgorithm": "KEY_ALG_RSA_2048",
            "keyOrigin": "GOOGLE_PROVIDED",
            "keyType": "SYSTEM_MANAGED",
            "name": "projects/[Project ID]/serviceAccounts/[name]@[Project ID].iam.gserviceaccount.com/keys/[key ID]",
            "validAfterTime": "2020-04-12T04:44:38Z",
            "validBeforeTime": "2020-04-29T04:44:38Z"
        }]

    https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-python
    """
    tracer = gcp_tracer
    with tracer.start_span(name=f"{app_name}:get_key({sa})") as span_method:
        service = googleapiclient.discovery.build('iam', 'v1')

        keys = service.projects().serviceAccounts().keys().list(name='projects/-/serviceAccounts/' + sa).execute()
        names = [key['name'] for key in keys['keys']]
        log(f"{app_name}:get_sa_keys {names}", severity=LOG_SEVERITY_DEBUG)

    return keys


def get_sa_keys_days_older(sa, days):
    """Lists keys for a USER_MANAGED service account over days old.
        Args:
            sa (str): Google Service Account.
            days (int): over given number of days old.

        Returns:
            keys of the Google Service Account over given number of days old:
            "keys": [
            {
                "keyAlgorithm": "KEY_ALG_RSA_2048",
                "keyOrigin": "GOOGLE_PROVIDED",
                "keyType": "USER_MANAGED",
                "name": "projects/[Project ID]/serviceAccounts/[name]@[Project ID].iam.gserviceaccount.com/keys/[key ID]",
                "validAfterTime": "2020-05-12T04:44:38Z",
                "validBeforeTime": "2020-05-29T04:44:38Z"
            }],
            "names": ["projects/[Project ID]/serviceAccounts/sa@[Project ID].iam.gserviceaccount.com/keys/fd4622af5e3e92df5633f95b7f2497a92751f004",
             "projects/[Project ID]/serviceAccounts/sa@[Project ID].iam.gserviceaccount.com/keys/dbb5f58c8b7f849bce9c24148dcfdc3f746b9170"]
    """
    days_float = float(days)
    keys = get_sa_keys(sa)
    keys = [item for item in keys['keys'] if item['keyType'] == 'USER_MANAGED']
    result_not_found = {
                           KEY_SA_KEY_DETAILS: [],
                           KEY_SA_KEY_NAMES: []
                       }, HTTPStatus.NOT_FOUND
    if not keys:
        return result_not_found

    days_older = [item for item in keys if
                  datetime.utcnow() - datetime.strptime(item['validAfterTime'], '%Y-%m-%dT%H:%M:%SZ') > timedelta(
                      days=days_float)]
    if not days_older:
        return result_not_found

    days_older_key_names = [item['name'] for item in days_older]
    names = days_older_key_names

    return {
        KEY_SA_KEY_DETAILS: days_older,
        KEY_SA_KEY_NAMES: names
    }


def delete_sa_keys_days_older(sa, days):
    keys_search_result = get_sa_keys_days_older(sa, days)
    if type(keys_search_result) is tuple:
        # something bad happened; the last item is the HTTP status code
        return {KEY_DELETED_SA: []}, keys_search_result[-1]

    deletion_result = delete_sa_keys_base(keys_search_result[KEY_SA_KEY_NAMES])

    return deletion_result


def err_to_resp(err):
    # Pass http errors to the client with the given HTTP code
    if isinstance(err, googleapiclient.errors.HttpError):
        return str(err), err.resp.status
    if isinstance(err, google.api_core.exceptions.GoogleAPIError):
        return str(err), err.code
    if hasattr(err, 'code'):
        return str(err), err.code
    # if the above cases can't handle the exception, throw server error
    return str(err), HTTPStatus.INTERNAL_SERVER_ERROR


key_thread_result_code = 'code'
key_thread_result = 'result'
key_thread_error = 'error'


def gen_sa_keys_add_secrets_delete_old_keys(days_float, service_accounts, secret_manager_project_id,
                                            secret_name_prefix):
    tracer = gcp_tracer
    method_name = 'gen_sa_keys_add_secrets'
    with tracer.start_span(name=f"{app_name}:{method_name}") as span_gen_sa_keys_add_secrets:
        def gen_key_put_secret(GCP_SA):
            with span_gen_sa_keys_add_secrets.span(name=f"{app_name}:{method_name}.gen_key({GCP_SA})") as span_gen_key:
                try:
                    GCP_SA_PROJECT_ID_search_result = re.search(SA_REGEX, GCP_SA)
                    GCP_SA_Name = GCP_SA_PROJECT_ID_search_result.group(1)
                    GCP_SA_PROJECT_ID = GCP_SA_PROJECT_ID_search_result.group(2)
                    sa_key = gen_key(GCP_SA)
                    secret_id = secret_name_prefix + GCP_SA_PROJECT_ID + "_" + GCP_SA_Name
                except Exception as ex:
                    error_reporting_client.report_exception()
                    result = {key_thread_error: str(ex)}
                    if isinstance(ex, google.api_core.exceptions.GoogleAPIError):
                        result[key_thread_result_code] = ex.code
                    if isinstance(ex, googleapiclient.errors.HttpError):
                        result[key_thread_result_code] = ex.resp.status

                    return result

                GCP_SA_dict = json.loads(sa_key)

            with span_gen_sa_keys_add_secrets.span(
                    name=f"{app_name}:{method_name}.put_secret({secret_id})") as span_put_secret:
                try:
                    find_secret_result, create_secret_result, add_secret_ver_result = put_secret(sa_key,
                                                                                                 secret_manager_project_id,
                                                                                                 secret_id)
                except Exception as ex:
                    error_reporting_client.report_exception()
                    key_name = f"projects/{GCP_SA_PROJECT_ID}/serviceAccounts/{GCP_SA}/keys/{GCP_SA_dict['private_key_id']}"
                    key_op = delete_sa_keys_base([key_name])
                    key_op['created'] = GCP_SA_dict
                    log(
                        f"{app_name}:{method_name} Failed to put secret for {GCP_SA_dict['client_email']}'s"
                        f" key {GCP_SA_dict['private_key_id']}, which was created then deleted",
                        severity=LOG_SEVERITY_WARNING)
                    result = {
                        key_thread_error: str(ex),
                        'handled': 'Google service account key created but could not put secret; key deleted',
                        KEY_SA_KEY_DETAILS: key_op
                    }
                    if isinstance(ex, google.api_core.exceptions.GoogleAPIError):
                        result[key_thread_result_code] = ex.code
                    if isinstance(ex, googleapiclient.errors.HttpError):
                        result[key_thread_result_code] = ex.resp.status

                    return result

                response = GCP_SA_dict
                if find_secret_result:
                    response['found_secret'] = find_secret_result.name
                if not find_secret_result and create_secret_result:
                    response['created_secret'] = create_secret_result.name
                if add_secret_ver_result:
                    response['added_secret_version'] = add_secret_ver_result.name

            if days_float > 0:
                with span_gen_sa_keys_add_secrets.span(
                        name=f"{app_name}:{method_name}.delete_old_keys({GCP_SA})") as span_delete_old_keys:
                    try:
                        deletion_result = delete_sa_keys_days_older(GCP_SA, days_float)
                        if type(deletion_result) is tuple:
                            if KEY_DELETED_SA in deletion_result[0]:
                                response[KEY_DELETED_SA] = deletion_result[0][KEY_DELETED_SA]
                            else:
                                response[KEY_DELETED_SA] = []
                        else:
                            response.update(deletion_result)

                    except Exception as ex:
                        error_reporting_client.report_exception()
                        result = {key_thread_error: str(ex)}
                        result.update(response)
                        if isinstance(ex, google.api_core.exceptions.GoogleAPIError):
                            result[key_thread_result_code] = ex.code
                        if isinstance(ex, googleapiclient.errors.HttpError):
                            result[key_thread_result_code] = ex.resp.status

                        return result

            return response

        with ThreadPoolExecutor(max_workers=int(MAX_WORKERS)) as executor:
            threads = [executor.submit(gen_key_put_secret, GCP_SA) for GCP_SA in service_accounts]
            futures.wait(threads, return_when=futures.ALL_COMPLETED)
    highest_http_code = HTTPStatus.OK
    success_counter = 0
    thread_results = []

    for t in threads:
        try:
            # exception thrown from .result() method if any exception happened
            if t.result():
                # check if anything bad happened in thread execution
                if key_thread_error in t.result():
                    if key_thread_result_code in t.result():
                        thread_results.append({
                            key_thread_result: t.result(),
                            key_thread_result_code: t.result()[key_thread_result_code]
                        })
                        # assign the highest http code to the response
                        if t.result()[key_thread_result_code] > highest_http_code:
                            highest_http_code = t.result()[key_thread_result_code]
                    else:
                        # unhandled error in thread results cause server error
                        highest_http_code = HTTPStatus.INTERNAL_SERVER_ERROR
                        thread_results.append({
                            key_thread_result: t.result(),
                            key_thread_result_code: HTTPStatus.INTERNAL_SERVER_ERROR
                        })
                else:
                    success_counter += 1
                    thread_results.append({
                        key_thread_result: t.result(),
                        key_thread_result_code: HTTPStatus.OK
                    })
        except Exception as ex:
            error_reporting_client.report_exception()
            msg, http_code = err_to_resp(ex)
            if http_code > highest_http_code:
                highest_http_code = http_code
            thread_results.append({
                key_thread_result: msg,
                key_thread_result_code: http_code
            })

    # full success
    if success_counter == len(threads):
        if days_float > 0:
            log(
                f"{app_name}:{method_name} generated keys > added them as secrets > deleted old keys for Google service accounts: {','.join(service_accounts)}",
                severity=LOG_SEVERITY_INFO)
        else:
            log(
                f"{app_name}:{method_name} generated keys > added them as secrets for Google service accounts: "
                f"{','.join(service_accounts)}", severity=LOG_SEVERITY_INFO)

    # partial success
    elif 0 < success_counter < len(threads):
        if days_float > 0:
            log(
                f"{app_name}:{method_name} generated keys > added them as secrets > deleted old keys for Google service accounts with partial success: "
                f"{','.join(service_accounts)}", severity=LOG_SEVERITY_WARNING)
        else:
            log(
                f"{app_name}:{method_name} generated keys > added them as secrets for Google service accounts with partial success: "
                f"{','.join(service_accounts)}", severity=LOG_SEVERITY_WARNING)

    # total failure
    else:
        if days_float > 0:
            log(
                f"{app_name}:{method_name} failed to generate keys > add them as secrets > delete old keys for Google service accounts: "
                f"{','.join(service_accounts)}", severity=LOG_SEVERITY_ERROR)
        else:
            log(
                f"{app_name}:{method_name} failed to generate keys > add them as secrets for Google service accounts: "
                f"{','.join(service_accounts)}", severity=LOG_SEVERITY_ERROR)

    # remove service account key JSON contents to prevent being logged at the invoker
    for result in thread_results:
        if key_thread_result in result and 'private_key' in result[key_thread_result]:
            del result[key_thread_result]['private_key']

    return jsonify(thread_results), highest_http_code
