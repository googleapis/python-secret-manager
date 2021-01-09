#!/bin/bash

# --headers Content-Type=application/json can't be created at Cloud Console at the time of the git commit.
# Manually creating the cloud scheduler causes the job to fail as application/json can't be specified.

set -e # exit the script when execution hits any error
set -x # print the executing lines

PROJECT_ID="must enter"
CLOUD_RUN_URL=`base cloud run url` # for https://*.a.run.app
GCP_SA_NAME=`service account name before @`
NAME=${PWD##*/}

gcloud scheduler jobs create http $NAME --schedule="0 0 * * *" --time-zone="America/New_York" \
  --message-body='{"secret-regex": "^hil"}'  --project $PROJECT_ID \
  --oidc-service-account-email=$GCP_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com --http-method=PUT \
  --oidc-token-audience=$CLOUD_RUN_URL --uri=$CLOUD_RUN_URL/projects/$PROJECT_ID/audit-secrets \
  --headers Content-Type=application/json