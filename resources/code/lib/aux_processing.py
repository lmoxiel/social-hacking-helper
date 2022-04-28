import os
import sys
import logging
import json
import datetime
import random
import time
import uuid
import aux

# ---------------------------------------------------------------------------------------------------------------------
# "Global variables" - what is the correct term for these things in Python?
# ---------------------------------------------------------------------------------------------------------------------

ENV_SNS_MESSAGE_EVENT_TOPIC_NAME = "SNS_MESSAGE_EVENT_TOPIC_NAME"
ENV_SNS_MESSAGE_EVENT_TOPIC_ARN = "SNS_MESSAGE_EVENT_TOPIC_ARN"

# ---------------------------------------------------------------------------------------------------------------------
# Publish SNS lambda event.
# ---------------------------------------------------------------------------------------------------------------------

def publish_sns_lambda_event(logger, event):
    logger.debug("Publish SNS event to ops topic.")
    topic_arn = os.environ.get(ENV_SNS_MESSAGE_EVENT_TOPIC_ARN, aux.STR_NONE)
    logger.debug("topic_arn: %s", topic_arn)
    return aux.publish_lambda_event(logger, event, topic_arn)

# ---------------------------------------------------------------------------------------------------------------------
