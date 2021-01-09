#!/bin/bash
set -e # exit the script when execution hits any error
set -x # print the executing lines

# follow commands at https://cloud.google.com/security-command-center/docs/how-to-notifications

PROJECT_ID="must enter"
NOTIF_NAME=service_account_key_not_rotated
ORGANIZATION_ID=`gcloud organizations list --format=json | jq '.[0] | .name' | awk '{split($0,org,"/"); print org[2]}' | sed -e 's/"$//'`
FILTER="category=\"SERVICE_ACCOUNT_KEY_NOT_ROTATED\" AND state=\"ACTIVE\""
PUBSUB_TOPIC="projects/$PROJECT_ID/topics/service_account_key_not_rotated"
PUBSUB_PROJECT=$PROJECT_ID
DESCRIPTION="Notifies for active category=SERVICE_ACCOUNT_KEY_NOT_ROTATED findings"

# The caller needs to have serviceusage.services.use permission
gcloud scc notifications create $NOTIF_NAME  \
   --organization "$ORGANIZATION_ID"   \
     --description "$DESCRIPTION"    \
      --pubsub-topic $PUBSUB_TOPIC   \
        --filter "$FILTER" \
        --project $PROJECT_ID