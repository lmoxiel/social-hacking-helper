import os
import sys
from enum import Enum, auto
import logging
import json
import datetime
import random
import time
import uuid
import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------------------------------------------------
# "Global variables" - what is the correct term for these things in Python?
# ---------------------------------------------------------------------------------------------------------------------

# Environment variables.
ENV_STAGE     = "STAGE"
ENV_WORKLOAD  = "WORKLOAD"
ENV_SERVICE   = "SERVICE"
ENV_LOG_LEVEL = "LOG_LEVEL"

STR_NONE = "NONE"

# Event keys.
EK_BODY = "body"

# Property keys, e.g. for DynamoDB items.
PK_CORRELATION_ID = "correlation-id"
PK_SUBMITTED_AT   = "submitted-at"
PK_UNICORN_ID     = "unicorn-id"
PK_CUSTOMER_ID    = "customer-id"
PK_RIDE_ID        = "ride-id"
PK_FARE           = "fare"
PK_DISTANCE       = "distance"

# ---------------------------------------------------------------------------------------------------------------------
# If the environment advises on a specific log level, set it accordingly.
# ---------------------------------------------------------------------------------------------------------------------

def update_log_level(logger, event, context):
    logger.debug("Checking for a directive for the log level in environment variable %s.", ENV_LOG_LEVEL)
    env_log_level = os.environ.get(ENV_LOG_LEVEL, STR_NONE)
    logger.debug("Found: %s", env_log_level)
    numeric_log_level = getattr(logging, env_log_level.upper(), None)
    if not isinstance(numeric_log_level, int):
        # If we didn't find a valid log level directive, let's stay with DEBUG.
        logger.debug("No valid directive found, so staying with DEBUG.")
        logger.setLevel(logging.DEBUG)
    else:
        # Adjust log level according to the directive we found.
        logger.debug("Adjusting log level to %d now.", numeric_log_level)
        logger.setLevel(numeric_log_level)

# ---------------------------------------------------------------------------------------------------------------------
# Log environment details.
# ---------------------------------------------------------------------------------------------------------------------

def log_env_details(logger):
    logger.debug("environment variables: %s", os.environ)

# ---------------------------------------------------------------------------------------------------------------------
# Log event and context details.
# ---------------------------------------------------------------------------------------------------------------------

def log_event_and_context(logger, event, context):
    logger.debug("event: %s", event)
    #logger.debug("context: %s", context)
    logger.debug("context: %s", vars(context))

# ---------------------------------------------------------------------------------------------------------------------
# Some timestamp helpers.
# ---------------------------------------------------------------------------------------------------------------------

class TimestampHelper:

    def __init__(self, logger):
        self.logger = logger
        self.ts = datetime.datetime.utcnow()
        self.log()

    def log(self):
        self.logger.debug("TimestampHelper: %s", self.ts.isoformat())

    def get_year(self):
        return self.ts.year
    def get_month(self):
        return self.ts.month
    def get_day(self):
        return self.ts.day
    def get_hour(self):
        return self.ts.hour

    def to_s3_path(self):
        return str(self.get_year()) + "/" + str(self.get_month()) + "/" + str(self.get_day())
    def to_s3_path_with_hour(self):
        return self.to_s3_path() + "/" + str(self.get_hour())

# ---------------------------------------------------------------------------------------------------------------------
# Publish Lambda event to respective ops topic.
# ---------------------------------------------------------------------------------------------------------------------

def publish_lambda_event(logger, event, topic_arn):
    try:
        logger.debug("Publish event to ops topic with ARN: %s", topic_arn)
        sns_client = boto3.client("sns")
        response = sns_client.publish(
            TargetArn = topic_arn,
            Message = json.dumps(event)
        )
    except Exception as ex:
        logger.exception("Something went wrong with publishing the event.")
        logger.exception(ex)
        return 0
    else:
        logger.debug("Event successfully published.")
        logger.debug("SNS response: %s", response)
        return 1

# ---------------------------------------------------------------------------------------------------------------------
