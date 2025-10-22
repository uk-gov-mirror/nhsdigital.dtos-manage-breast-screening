#!/usr/bin/env bash

set -euo pipefail

ENV=$1
JOB_SHORT_NAME=${2}
JOB_NAME=manbrs-${JOB_SHORT_NAME}-${ENV}

RG_NAME=rg-manbrs-${ENV}-container-app-uks
TIMEOUT=300
WAIT=5
count=0

get_job_status() {
    az containerapp job execution show --job-execution-name "$execution_name" -n "$JOB_NAME" -g "$RG_NAME" | jq -r '.properties.status'
}

echo Starting job "$JOB_NAME"...

if [ "$JOB_SHORT_NAME" = "crp" ]; then
  echo "Creating smoke test reports"
  execution_name=$(az containerapp job start --image "ghcr.io/nhsdigital/dtos-manage-breast-screening:cache-notifications-smoke-test" --name "$JOB_NAME" --resource-group "$RG_NAME" --args "python" "manage.py" "create_reports" "--smoke-test" | jq -r '.id|split("/")[-1]')
else
  execution_name=$(az containerapp job start --name "$JOB_NAME" --resource-group "$RG_NAME" | jq -r '.id|split("/")[-1]')
fi

while [[ $(get_job_status) = "Running" ]]; do
    echo The job "$execution_name" is still running...
    ((count*WAIT > TIMEOUT)) && break
    ((count+=1))
    sleep $WAIT
done

if ((count*WAIT > TIMEOUT)); then
    echo "The job \"$execution_name\" timed out (${TIMEOUT}s)"
    exit 1
fi

status=$(get_job_status)
if [[ $status = "Succeeded" ]]; then
    echo The job "$execution_name" completed successfully
else
    echo The job "$execution_name" has not completed successfully. Status: "$status"
    exit 2
fi
