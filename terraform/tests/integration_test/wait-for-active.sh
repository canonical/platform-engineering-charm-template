#!/bin/bash
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

MODEL_UUID=$1
APP_NAME=$2

LOG="/tmp/wait-for-active.$$.log"

if [ -z "$MODEL_UUID" -o -z "$APP_NAME" ]; then
	echo "Usage: $0 <model_uuid|model_name> <app_name>"
	echo "[$(date)] missing arguments" >> $LOG
	exit 1
fi

if ! juju show-model "$MODEL_UUID" &> /dev/null; then
	echo '{"status": "model_not_found"}'
	echo "[$(date)] model not found: $MODEL_UUID" >> $LOG
	exit
fi

if ! juju show-application "$APP_NAME" &> /dev/null; then
	echo '{"status": "app_not_found"}'
	echo "[$(date)] app not found: $APP_NAME" >> $LOG
	exit
fi

juju wait-for application "$APP_NAME" --timeout=1m &>> $LOG
STATUS=$(juju status "$APP_NAME" --model "$MODEL_UUID" --format=json | jq -r '.applications | to_entries[0].value["application-status"].current')

echo '{"status": "'"$STATUS"'"}'
