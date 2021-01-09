import os
import re
import sys
from http import HTTPStatus

from flask import Flask
from flask import request
from gcloud import pubsub  # used to get project ID
from google.cloud import error_reporting

import backend

SEPARATOR = ","

KEY_DELETED_SA = 'deleted'
KEY_SA_KEY_NAMES = 'names'
KEY_SA_KEY_DETAILS = 'keys'
SA_REGEX = '^([\w-]+)@([\w-]+)\.iam\.gserviceaccount\.com$'
SECRET_REGEX = '^[\w-]+$'

try:
    import googleclouddebugger

    googleclouddebugger.enable()
except:
    for e in sys.exc_info():
        print(e)

app = Flask(__name__)

# if debugging or running on localhost
if __name__ == "__main__":
    gcp_project_id = os.environ['GCP_PROJECT']
# running in Google Cloud Run
else:
    pubsub_client = pubsub.Client()
    gcp_project_id = pubsub_client.project

error_reporting_client = error_reporting.Client()


@app.route('/health', methods=['GET'])
def health_check():
    import flask
    return 'Running Flask {0} on Python {1}!\n'.format(flask.__version__, sys.version)


# full stacktrace is in Cloud Error reporting
@app.errorhandler(Exception)
def handle_uncaught_exception(err):
    error_reporting_client.report_exception()
    return backend.err_to_resp(err)


@app.route('/projects/<secret_manager_project_id>/audit-secrets', methods=['PUT'])
def audit_secrets(secret_manager_project_id):
    key_secret_regex = 'secret-regex'

    request_body = request.get_json()
    if request_body and key_secret_regex in request_body:
        results = backend.audit_secrets_sa(secret_manager_project_id, request_body[key_secret_regex])
    else:
        return f"Missing json request body with key: {key_secret_regex} or value is empty", HTTPStatus.BAD_REQUEST

    highest_http_status = HTTPStatus.OK
    for key in results:
        if isinstance(results[key], Exception):
            # convert the Exception to string
            msg, http_status = backend.err_to_resp(results[key])
            results[key] = msg
            if http_status > highest_http_status:
                highest_http_status = http_status

    if highest_http_status > HTTPStatus.OK:
        return results, highest_http_status
    else:
        return results


@app.route('/gen-sa-keys-add-secrets/delete-keys-days-old/<days>', methods=['PUT'])
def gen_sa_keys_add_secrets(days):
    """
    Generate Google service account keys and add them to secrets. Then delete Google service account keys older than
    passed number of days in the path parameter.
      Accept a list of Google service accounts in the header,
      a floating point number of days old keys to delete in the path.
    Secret Manager Admin role is required to create new secret name in secret_manager_project_id
    1. Create a Google service account keys from request body.form-data.GCP_SAs
    2. put in secret manager as secret IDs of <secret_name_prefix><PROJECT_ID>_<SA_NAME>
    3. Delete keys older than specified floating number of days. 0 means do not delete keys.

    Args:
        GCP_SAs (header form-data): Google Service Account separated by ,
        secret_name_prefix (header form-data): prefix of secret ID in secret manager
        secret_manager_project_id (header form-data): secret manager's PROJECT ID. If not specified,
         use an environment variable at local debugging or the current project in Cloud Run.
        days (path parameter): floating point number of days; 0 means don't delete keys.

    Returns:
        highest HTTP status code from thread.result()
        In each completed thread, examin the thread result['error'], result['code']
    """

    days_float = float(days)
    # parsing the form-data from the request header
    form_key_GCP_SAs = 'GCP_SAs'
    if form_key_GCP_SAs not in request.form or not request.form[form_key_GCP_SAs]:
        return 'Missing form-data of key: {0} or value empty'.format(form_key_GCP_SAs), HTTPStatus.BAD_REQUEST

    form_key_secret_prefix = 'secret_name_prefix'
    if form_key_secret_prefix not in request.form or not request.form[form_key_secret_prefix]:
        secret_name_prefix = ''
    else:
        secret_name_prefix = request.form[form_key_secret_prefix]
        regex_search_result = re.search(SECRET_REGEX, secret_name_prefix)
        if not regex_search_result:
            return 'Secret names can only contain English letters (A-Z), numbers (0-9), dashes (-), ' \
                   'and underscores (_)', HTTPStatus.BAD_REQUEST

    form_key_secret_manager_project_id = 'secret_manager_project_id'
    if form_key_secret_manager_project_id not in request.form \
            or not request.form[form_key_secret_manager_project_id]:
        secret_manager_project_id = gcp_project_id
    else:
        secret_manager_project_id = request.form[form_key_secret_manager_project_id]

    # sanity check of the Google service account format
    service_accounts = request.form[form_key_GCP_SAs].split(SEPARATOR)
    for sa in service_accounts:
        regex_search_result = re.search(SA_REGEX, sa)
        if not regex_search_result or len(regex_search_result.groups()) != 2:
            return f"At least 1 Google service account in form-data of key {form_key_GCP_SAs} fails" \
                   f" regular expression of {SA_REGEX}: {sa}", HTTPStatus.BAD_REQUEST

    return backend.gen_sa_keys_add_secrets_delete_old_keys(days_float, service_accounts, secret_manager_project_id,
                                                           secret_name_prefix)


@app.route('/sa/<sa>/keys-days-older/<days>', methods=['DELETE'])
def delete_sa_keys_days_older(sa, days):
    return backend.delete_sa_keys_days_older(sa, days)


@app.route('/sa-keys', methods=['DELETE'])
def delete_sa_keys():
    """Delete GSA keys passed in the request form data as a list"""
    form_key = 'sa-key-names'
    if form_key not in request.form or not request.form[form_key]:
        return 'Missing form-data of key: {0} or value empty'.format(form_key), HTTPStatus.BAD_REQUEST

    full_sa_key_names = request.form[form_key].split(',')

    try:
        return backend.delete_sa_keys_base(full_sa_key_names)
    except ValueError as err:
        return f"Google service account key in form-data of key {form_key} isn't in the format of " \
               f"projects/PROJECT_ID/serviceAccounts/sa@PROJECT_ID.iam.gserviceaccount.com/keys/key_name: " \
               f"{str(err)}", HTTPStatus.BAD_REQUEST


@app.route('/sa/<sa>/keys-days-older/<days>', methods=['GET'])
def get_sa_keys_days_older(sa, days):
    return backend.get_sa_keys_days_older(sa, days)


@app.route('/sa/<sa>/keys', methods=['GET'])
def get_sa_keys(sa):
    return backend.get_sa_keys(sa)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
