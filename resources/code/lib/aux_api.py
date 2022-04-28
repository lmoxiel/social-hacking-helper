import os
import sys
import logging
import json
import datetime
import random
import time
import uuid
import aux
import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------------------------------------------------
# "Global variables" - what is the correct term for these things in Python?
# ---------------------------------------------------------------------------------------------------------------------

ENV_APIGW_REQUEST_EVENT_TOPIC_NAME = "APIGW_REQUEST_EVENT_TOPIC_NAME"
ENV_APIGW_REQUEST_EVENT_TOPIC_ARN = "APIGW_REQUEST_EVENT_TOPIC_ARN"

ENV_RIDES_STORE_TABLE_NAME = "RIDES_STORE_TABLE_NAME"

BAD_REQUEST_NO_JSON_BODY = "Request body doesn't seem to be a JSON document."

# ---------------------------------------------------------------------------------------------------------------------
# Publish API GW lambda event.
# ---------------------------------------------------------------------------------------------------------------------

def publish_apigw_lambda_event(logger, event):
    logger.debug("Publish API GW event to ops topic.")
    topic_arn = os.environ.get(ENV_APIGW_REQUEST_EVENT_TOPIC_ARN, aux.STR_NONE)
    logger.debug("topic_arn: %s", topic_arn)
    return aux.publish_lambda_event(logger, event, topic_arn)

# ---------------------------------------------------------------------------------------------------------------------
# Prepare a "400 Bad Request" response.
# ---------------------------------------------------------------------------------------------------------------------

def bad_request(LOGGER, event, message, ex):

    data = {
        "links": {
            "TBD": "http://..."
        },
        "message": BAD_REQUEST_NO_JSON_BODY,
        "request-body": event[aux.EK_BODY]
    }

    return {
        "statusCode": 400,
        "body": json.dumps(data),
        "headers": {
            "Content-Type": "application/json"
        }
    }

# ---------------------------------------------------------------------------------------------------------------------
# Capture (and log) the current timestamp as the one the ride completion was submitted.
# ---------------------------------------------------------------------------------------------------------------------

def create_submitted_at(logger):
    submitted_at = datetime.datetime.utcnow().isoformat()
    logger.debug("submitted_at: %s", submitted_at)
    return submitted_at

# ---------------------------------------------------------------------------------------------------------------------
# Create a correlation ID.
# ---------------------------------------------------------------------------------------------------------------------

def create_correlation_id(logger):
    correlation_id = str(uuid.uuid4())
    logger.debug("correlation_id: %s", correlation_id)
    return correlation_id

# ---------------------------------------------------------------------------------------------------------------------
