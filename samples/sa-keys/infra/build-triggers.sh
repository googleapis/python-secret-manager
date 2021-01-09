#!/bin/bash
set -e # exit the script when execution hits any error
set -x # print the executing lines


NAME=${PWD##*/}
REPO_NAME=hil.liao
BRANCH=dev
REPO_PATH="googlecloud/${PWD##*/}"
TOPIC=service_account_key_not_rotated
CLOUD_RUN_URL=https://.a.run.app

gcloud beta builds triggers create cloud-source-repositories \
    --repo=$REPO_NAME --name=$NAME \
    --branch-pattern="^$BRANCH$" \
    --build-config="$REPO_PATH/cloudbuild.yaml" \
    --included-files="$REPO_PATH/**" \
    --ignored-files="**/README.md,$REPO_PATH/infra/**,$REPO_PATH/func/**,**/unittests.py" \
    --substitutions _CLOUD_RUN_SVC_NAME=${PWD##*/},_GCP_SA=sa-keys-admin,_MAX_THREADS=22 && \
gcloud beta builds triggers create cloud-source-repositories \
    --repo=$REPO_NAME --name="$NAME-func" \
    --branch-pattern="^$BRANCH$" \
    --build-config="$REPO_PATH/func/cloudbuild.yaml" \
    --included-files="$REPO_PATH/func/**" \
    --ignored-files="**/README.md,**/unittests.py" \
    --substitutions _CLOUD_RUN_URL=$CLOUD_RUN_URL,_GCP_SA=sa-keys-invoker,_TOPIC=$TOPIC,_FUNC="$NAME-func"