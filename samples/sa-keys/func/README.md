# Google service account key management service client

A cloud function that calls the Key management service in cloud run with a pub/sub trigger. 

## Getting Started

0. Refer to the parent folder's README for deployment manager related execution steps.
0. The infra/func*.yaml is the deployment needed to create the service account for the cloud function.

### Set up the local development environment

0. Generate a JSON key file for the service account the infra/func*.yaml deployment created.
0. set GOOGLE_APPLICATION_CREDENTIALS environment variable to that key file's path. Make sure the SA has cloud run
invoker role to the configured cloud run service.
0. set PROJECT_ID environment variable to the test service account's Project ID used for testing locally.
0. set GCP_SA environment variable to the test service account name before `@`, used for testing locally.
0. set DELIMITER environment variable to `,`
0. set FIRESTORE_COLLECTION to the value of app_name variable
0. set FIRESTORE_DOC to the config Firestore doc ID
0. Examine unittests.py's first few lines to set required environment variables

### Configure CI CD pipelines with cloud build and source repository

0. Edit cloud build trigger command at googlecloud/sa-keys/infra/build-triggers.sh
      - provide the correct substitution values for _CLOUD_RUN_URL, which is the deployed cloud run service URL.
      - provide the correct substitution values for _GCP_SA, the service account created from infra/func*.yaml 
        resources.name[].properties.service-account
      - provide the correct substitution values for _TOPIC so the cloud function will be triggered by the topic. 
        set the value to be infra/func*.yaml resources.name[].properties.topic  
      - set the environment variables for the trigger name, repo, branch
0. Bind Cloud run invoker role to the cloud function's Google service account under
 the deployed Key management cloud run service.

### Prerequisites

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

### Installing

Clone the code to your cloud source repository. With Cloud build trigger
configured per infra/build-triggers.sh, pushing to the cloud source repository will trigger the
build and deployment to Cloud Run. Verify Cloud Run is enabled in your
project. In Cloud Build's trigger, substitute variables of name starting with $`_` in
cloudbuild.yaml for Cloud run related customization.

#### Firestore function config document
Create a collection with the name of app_name's value defaulting to `sa-keys-func`. Then create a document named
`config` containing the fields:
* SA-regex: String # only service account matching the regular expression will be processed
* cloud_run: String # Cloud run URL like https://sa-keys-REDACTED-uc.a.run.app
* gen-sa-keys-add-secrets/delete-keys-days-old/0.000694444: String # subpath to the cloud_run url
* cloud_run_verb: String # HTTP verb to invoke the cloud run url with
* project_id_regex: String # only service account where its project ID matching the regular expression will be processed
* secret_manager_project_id: String # form data's key to invoke cloud run service with 

### Basic testing

Call the health endpoint
use postman or
```
curl --request GET 'https://sakeys-uc.a.run.app/health' \
--header 'Authorization: Bearer $TOKEN'
```

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

## Deployment

Inspect the Cloud trace, Cloud Debugger, Cloud Logging to see invoking
the endpoints create the trace, logs, and an active debugging
application. the latency for the trace or logs to show is usually 2
minutes; setting a snapshot in the Cloud Debugger and hitting the
endpoint may not catch a snapshot right away. Maybe there was some lag.
It's usually the 2nd time of hitting the endpoint to catch the snapshot.

## License

This project is licensed under [Apache License, Version 2.0 (Apache 2.0)](http://www.apache.org/licenses/LICENSE-2.0)