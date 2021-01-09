# Google service account key management solution

A microservice deployed in Google Cloud Run that manages an
existing Google service account's keys. Implementation contains
GET to list the keys, POST to create keys and store in secret
manager, DELETE to remove keys.

## Getting Started

0. [Bind project owner role to Google APIs service account](https://cloud.google.com/deployment-manager/docs/configuration/set-access-control-resources##granting_permission_to_set_iam_policies)
 in order to create deployments in deployment manager
0. Bind Deployment Manager Editor role to your Google account
0. Replace DEPL_NAME with a deployment name, FILENAME with each *.yaml files, then execute the command 
```shell script
gcloud config  set project PROJECT_ID
gcloud deployment-manager deployments create DEPL_NAME --config infra/FILENAME.yaml
```
0. Inspect [the deployment's result](https://console.cloud.google.com/dm/deployments)

## Set up the local development environment

0. Generate a JSON key file for the service account the infra/svc*.yaml deployment created.
0. set GOOGLE_APPLICATION_CREDENTIALS environment variable to that key file's path.
0. set GCP_PROJECT environment variable to the Google cloud Project ID for secret manager
0. set PORT environment variable for the Python flask application.
0. Examine unittests.py's first few lines to set required environment variables

## Configure CI CD pipelines with cloud build and source repository

0. Edit cloud build trigger command at googlecloud/sa-keys/infra/build-triggers.sh
      - provide the correct substitution values for _GCP_SA; inspect the deployment results for the service account used
      for the cloud run service.
      - provide the desired substitution values for _CLOUD_RUN_SVC_NAME, the name of the cloud run service
      - provide the desired substitution values for _MAX_THREADS used in Python ThreadPoolExecutor(max_workers=MAX_WORKERS
      - set the environment variables for the trigger name, repo, branch
0. [Bind Cloud Run Admin role to Cloud build service account](https://console.cloud.google.com/cloud-build/settings/service-account)
0. Under the deployed cloud run service, bind Cloud Run invoker role to the cloud function's service account, 
developer's Google account, or operation team's Google group who invoke the Cloud Run service.
0. Be aware the requirements.txt may use the latest version of python packages which may be incompatible to each other.
Execute the following command to test installed packages in docker build. Compare with python virtual environment's
pip3 list output to check versions.
```shell script
docker run --rm --name tmp  -p 81:8080 -e PORT=8080 -it gcr.io/$PROJECT_ID/sa-keys  pip3 list
```

## Prerequisites

Python 3.8 requirements.txt shows required Python modules for the app to
run. Example python development environment creation steps:

```
$ python3 -m venv .
$ . bin/python
$ python --version # verify the python version is 3.x
$ pip install -r requirements.txt
```
If PORT environment variable is not set, app will run on 8080. Make sure
the port is free to use. The main module is
manager.py which you should select in Pycharm's debug configuration.

## Installing

Clone the code to your cloud source repository. With Cloud build trigger
configured, pushing to the cloud source repository will trigger the
build and deployment to Cloud Run. Verify Cloud Run is enabled in your
project. In Cloud Build's trigger, substitute variables of name starting with $`_` in
cloudbuild.yaml for Cloud run related customization.

Inspect script contents in files under the infra folder to check manual steps required before or after execution.
For example, logs-router.sh informs manual dataset IAM role binding after execution.

### scheduled-job.sh
Create scheduled job to call Cloud Run Audit endpoint to scan secrets. Change --message-body
to the regular expression of secrets to be audited.
### logs-router.sh
Create a log sink to write logs to BigQuery. Must have Logs Configuration Writer IAM role to execute.
### scc_notifications_create.sh
Create security command center pub/sub notifications. Follow the link in the script that
has a series of gcloud commands to execute before running the script.

## Basic testing

Call the health endpoint
use postman or
```
curl --request GET 'https://sakeys-uc.a.run.app/health' \
--header 'Authorization: Bearer $TOKEN'
```
Check cloud error reporting for errors and exceptions as developers see 500 server error in HTTP response.

## Running the tests

Import ../*postman_collection.json into Postman for easy invocation of the REST methods.

0. set {{url}} to the cloud run url including https://
0. set {{id_token}} to the output of gcloud auth
   print-identity-token from the Google Account with Cloud Run invoker
   role bound to the cloud run service.
0. set {{GSA}}, {{GSA1}} to be the testing Google service account
0. set {{keys}} to be Google service account full key names separated by `,`: projects/PROJECT_ID/serviceAccounts/GCP_SA@PROJECT_ID.iam.gserviceaccount.com/keys/key_name
0. set {{PROJECT_ID}} to be the secret manager's project ID
0. Endpoint {{url}}/rotate_days_old/{{number_of_days}} is the primary method that rotates Google service account keys

## Instrumentation

Inspect the Cloud trace, Cloud Debugger, Cloud Logging to see invoking
the endpoints create the trace, logs, and an active debugging
application. the latency for the trace or logs to show is usually 2
minutes; setting a snapshot in the Cloud Debugger and hitting the
endpoint may not catch a snapshot right away. Maybe there was some lag.
It's usually the 2nd time of hitting the endpoint to catch the snapshot.

## Known issues
one of the dependent python package `jquery - jquery/jquery,3.4.1` may have vulnerabilities:
0. [CVE-2020-11022](https://nvd.nist.gov/vuln/detail/CVE-2020-11022) In jQuery versions greater than or equal to 1.2 and before 3.5.0, passing HTML from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code. This problem is patched in jQuery 3.5.0.
0. [CVE-2020-11023](https://nvd.nist.gov/vuln/detail/CVE-2020-11023) In jQuery versions greater than or equal to 1.0.3 and before 3.5.0, passing HTML containing elements from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code. This problem is patched in jQuery 3.5.0.	

## License

This project is licensed under [Apache License, Version 2.0 (Apache 2.0)](http://www.apache.org/licenses/LICENSE-2.0)