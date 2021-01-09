import base64
import json
import os
import re
from http import HTTPStatus

import google.auth
import google.auth.transport.requests
from google.auth import compute_engine
from google.auth.transport.requests import AuthorizedSession
from google.cloud import firestore
from google.cloud import logging
from google.oauth2 import id_token
from google.oauth2 import service_account

CLOUD_FUNC_KEY_DATA = 'data'
app_name = 'sa-keys-func'
LOG_SEVERITY_DEFAULT = 'DEFAULT'
LOG_SEVERITY_INFO = 'INFO'
LOG_SEVERITY_ERROR = 'ERROR'
LOG_SEVERITY_WARNING = 'WARNING'
LOG_SEVERITY_DEBUG = 'DEBUG'
SA_postfix = ".iam.gserviceaccount.com"
SA_regex = '([\w@-]+)' + SA_postfix.replace(".", "\.") + '$'

# method return dict keys
key_abort_level = 'abort_level'
key_payload = 'payload'

# firestore document fields
key_secret_project_id = 'secret_manager_project_id'
key_projectid_regex = 'project_id_regex'
key_SA_regex = 'SA-regex'
key_cloud_run_subpath = 'cloud_run_subpath'
key_cloud_run_verb = 'cloud_run_verb'
key_cloud_run_url = 'cloud_run'


def log(text, severity=LOG_SEVERITY_DEFAULT, log_name=app_name):
    logging_client = logging.Client()
    logger = logging_client.logger(log_name)

    return logger.log_text(text, severity=severity,
                           resource=google.cloud.logging.Resource(type="cloud_function",
                                                                  labels={}))


# test publishing message to the topic:
# {"resource": {"parentDisplayName": "projects/$PROJECT_ID/serviceAccounts/sa@$PROJECT_ID.iam.gserviceaccount.com"}}
# method name needs to be the value of --entry-point in cloudbuild.yaml
def process_key(message, context):
    if context:
        print("""This Function was triggered by messageId {} published at {}""".format(context.event_id,
                                                                                       context.timestamp))

    if CLOUD_FUNC_KEY_DATA in message:
        data = base64.b64decode(message[CLOUD_FUNC_KEY_DATA]).decode('utf-8')
        log(f"event dict data key has value: {data}", severity=LOG_SEVERITY_DEBUG)
    else:
        raise LookupError(f"event dict does not contain data key: {message}")

    SA_key_not_rotated = json.loads(data)
    key_resource = "resource"
    if key_resource not in SA_key_not_rotated:
        raise LookupError(f"Security command center finding dict does not contain key {key_resource}")

    resource = SA_key_not_rotated[key_resource]
    key_parentDisplayName = "parentDisplayName"
    if key_parentDisplayName not in resource:
        raise LookupError(f"Security command center finding dict does not contain key {key_parentDisplayName}")

    # extract SA from parentDisplayName
    project_SA_REGEX = 'projects/([\w-]+)/serviceAccounts/' + SA_regex
    parentDisplayName = resource[key_parentDisplayName]
    parentDisplayName_regex_search_result = re.search(project_SA_REGEX, parentDisplayName)
    if not parentDisplayName_regex_search_result or len(parentDisplayName_regex_search_result.groups()) != 2:
        raise ValueError(
            f"finding.{key_resource}.{key_parentDisplayName} failed to match regular expression {project_SA_REGEX}")

    GCP_SA = parentDisplayName_regex_search_result.group(2) + SA_postfix
    project_id = parentDisplayName_regex_search_result.group(1)
    log(f"extracted Google service account is {GCP_SA} and project ID is {project_id}", severity=LOG_SEVERITY_DEBUG)

    result = verify_config(GCP_SA, project_id, get_config_func=get_or_init_config)
    if result[key_abort_level] != 0:
        return result[key_payload]

    secret_project_id = result[key_payload][key_secret_project_id]

    # create an authenticated request to Cloud run GSA key manager for key rotation
    google_oauth_request = google.auth.transport.requests.Request()
    target_audience = result[key_payload][key_cloud_run_url]
    url = f"{result[key_payload][key_cloud_run_url]}/{result[key_payload][key_cloud_run_subpath]}"

    # local debugging vs executing in Google cloud
    if 'GCP_SA' in os.environ:
        creds = service_account.IDTokenCredentials.from_service_account_file(
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'], target_audience=target_audience)
    else:
        creds = compute_engine.IDTokenCredentials(google_oauth_request,
                                                  target_audience=target_audience,
                                                  use_metadata_identity_endpoint=True)

    authed_session = AuthorizedSession(creds)
    form_data = {
        'GCP_SAs': GCP_SA,
        # 'secret_name_prefix': 'hil_0_',
        key_secret_project_id: secret_project_id
    }
    sa_key_manager_response = authed_session.request(result[key_payload][key_cloud_run_verb], url=url, data=form_data)

    func_response = {
        'content': sa_key_manager_response.content.decode('utf-8'),
        'reason': sa_key_manager_response.reason,
        'status_code': sa_key_manager_response.status_code,
    }

    # on success, response has json method
    if sa_key_manager_response.status_code == HTTPStatus.OK:
        func_response['content'] = sa_key_manager_response.json()

    # show security tokens at local debugging
    if 'GCP_SA' in os.environ:
        google_oauth_request = google.auth.transport.requests.Request()
        func_response['identity_token'] = creds.token
        func_response['Open ID Connect token verification'] = id_token.verify_token(creds.token,
                                                                                    google_oauth_request)
    else:
        log(f"Calling {result[key_payload][key_cloud_run_url]} returns: {json.dumps(func_response)}", severity='DEBUG')

    return func_response


def verify_config(GCP_SA, project_id, get_config_func):
    # get and apply configurations from Firestore
    config, config_doc_path = get_config_func()
    firestore_config_keys = [key_projectid_regex,
                             key_SA_regex,
                             key_cloud_run_url,
                             key_cloud_run_verb,
                             key_cloud_run_subpath,
                             key_secret_project_id]

    if not config:
        err = f"Failed to load configurations at {config_doc_path}"
        log(err, severity=LOG_SEVERITY_ERROR)
        return {key_abort_level: LOG_SEVERITY_ERROR, key_payload: err}

    # check config key fields exist in firestore doc
    for key in firestore_config_keys:
        if key not in config:
            err = f"Firestore document at {config_doc_path} does not have field {key}"
            log(err, severity=LOG_SEVERITY_ERROR)
            return {key_abort_level: LOG_SEVERITY_ERROR, key_payload: err}

    # verify the service account matches the regular expression in Firestore config
    regex_search_result = re.search(config[key_SA_regex], GCP_SA)
    if regex_search_result:
        log(f"{GCP_SA} matched regular expression {config[key_SA_regex]}", severity=LOG_SEVERITY_DEBUG)
    else:
        warning = f"{GCP_SA} did NOT match regular expression {config[key_SA_regex]}"
        log(warning, severity=LOG_SEVERITY_WARNING)
        return {key_abort_level: LOG_SEVERITY_WARNING, key_payload: warning}

    # verify the SA's project ID against project ID regex in Firestore config
    projectid_regex_search_result = re.search(config[key_projectid_regex], project_id)

    if projectid_regex_search_result:
        log(f"Project ID {project_id} matched regular expression {config[key_projectid_regex]}",
            severity=LOG_SEVERITY_DEBUG)
    else:
        warning = f"Project ID {project_id} did NOT matched regular expression {config[key_projectid_regex]}"
        log(warning, severity=LOG_SEVERITY_WARNING)
        return {key_abort_level: LOG_SEVERITY_WARNING, key_payload: warning}

    return {
        key_abort_level: 0,
        key_payload: config
    }


def get_or_init_config(collection=os.getenv('FIRESTORE_COLLECTION', app_name),
                       config_doc_id=os.getenv('FIRESTORE_DOC', 'config')):
    firestore_client = firestore.Client()
    config_snapshot_doc = firestore_client.collection(collection).document(config_doc_id).get()
    config = config_snapshot_doc.to_dict()

    # config document absent; create new
    if not config:
        undefined = 'undefined'
        writeResult = firestore_client.collection(collection).document(config_doc_id).set({
            key_cloud_run_url: undefined,
            key_cloud_run_verb: undefined,
            key_cloud_run_subpath: undefined,
            key_projectid_regex: f"^{undefined}$",
            key_SA_regex: f"^{undefined}@\.iam\.gserviceaccount\.com$",
            key_secret_project_id: undefined,
        })
        log(f"Created Firestore collection {collection}, document {config_doc_id}: {str(writeResult)}",
            severity=LOG_SEVERITY_DEBUG)
        config_snapshot_doc = firestore_client.collection(collection).document(config_doc_id).get()
        config = config_snapshot_doc.to_dict()

    config_doc_path = config_snapshot_doc.reference.path
    return config, config_doc_path


if __name__ == "__main__":
    msg = {
        "resource": {
            "parentDisplayName": f"projects/{os.environ['PROJECT_ID']}/serviceAccounts/{os.environ['GCP_SA']}"
        }
    }
    encodedBytes = base64.b64encode(json.dumps(msg).encode('utf-8'))
    print(process_key({CLOUD_FUNC_KEY_DATA: encodedBytes}, None))
