#!/bin/bash
set -e # exit the script when execution hits any error
set -x # print the executing lines

PROJECT_ID="must enter"
DATASET=service_account_audit
FILTER="resource.type=\"cloud_run_revision\" log_name=\"projects/$PROJECT_ID/logs/${PWD##*/}-audit\""
SINK=bigquery.googleapis.com/projects/$PROJECT_ID/datasets/$DATASET
NAME=${PWD##*/}-audit
DESC="Audit secrets to verify service account keys"

gcloud alpha logging sinks create $NAME $SINK --project $PROJECT_ID \
  --log-filter="$FILTER" --description="$DESC" && \
bq  mk  --dataset --description="$DESC" $PROJECT_ID:$DATASET && \
writer_SA=`gcloud alpha logging sinks describe ${PWD##*/}-audit --project $PROJECT_ID --format json|jq '.writerIdentity'` && \
echo "Grant $writer_SA BigQuery Data Editor role in dataset $DATASET in project $PROJECT_ID"