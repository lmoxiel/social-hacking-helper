import os
import logging
import json
import urllib.parse
import boto3
import aux
import aux_paths
import aux_eventbridge_events

# --------------------------------------------------------------------------------------------------
# Globals.
# --------------------------------------------------------------------------------------------------

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

S3_CLIENT = boto3.client("s3")

ENV_CONTACT_CENTER_DATA_BUCKET_ARN  = "CONTACT_CENTER_DATA_BUCKET_ARN"
ENV_CONTACT_CENTER_DATA_BUCKET_NAME = "CONTACT_CENTER_DATA_BUCKET_NAME"
ENV_DATA_LAKE_DATA_BUCKET_ARN  = "DATA_LAKE_DATA_BUCKET_ARN"
ENV_DATA_LAKE_DATA_BUCKET_NAME = "DATA_LAKE_DATA_BUCKET_NAME"

# --------------------------------------------------------------------------------------------------
# Functions.
# --------------------------------------------------------------------------------------------------

def construct_destination_object_key(logger, source_object_key):
    """
    Based on the object key of the new Amazon Connect call recording, construct the object key for
    ingestion of the new call recording into the data lake bucket.
    """

    # Extract substring of source object key after CallRecordings/
    index = source_object_key.find(aux_paths.PATH_CONNECT_CALLRECORDINGS)
    logger.debug("Index of %s is: %d", aux_paths.PATH_CONNECT_CALLRECORDINGS, index)
    index = index + len(aux_paths.PATH_CONNECT_CALLRECORDINGS)
    logger.debug("Index of next character after %s is: %d",
        aux_paths.PATH_CONNECT_CALLRECORDINGS, index
    )
    tmp_destination_object_key_suffix = source_object_key[index:]
    logger.debug("tmp_destination_object_key_suffix: %s", tmp_destination_object_key_suffix)
    # Reformat the timestamp in the object key, after the call-id.
    destination_object_key_suffix = tmp_destination_object_key_suffix[:52] + "-" + tmp_destination_object_key_suffix[52:54] + "-" + tmp_destination_object_key_suffix[54:62] + ":00Z.wav"
    logger.debug("destination_object_key_suffix: %s", destination_object_key_suffix)
    destination_object_key = aux_paths.PATH_CONNECT_CALLRECORDINGS_RAW + destination_object_key_suffix
    logger.debug("destination_object_key: %s", destination_object_key)
    return destination_object_key

# --------------------------------------------------------------------------------------------------

def lambda_handler(event, context):
    """
    Copy a new call recording from the contact center bucket to the data lake bucket.
    """
    # If the environment advises on a specific debug level, set it accordingly.
    aux.update_log_level(LOGGER, event, context)
    # Log environment details.
    aux.log_env_details(LOGGER)
    # Log request details.
    aux.log_event_and_context(LOGGER, event, context)

    # Extract the AWS account ID where this Lambda function is running.
    aws_account_id = context.invoked_function_arn.split(":")[4]
    LOGGER.debug("aws_account_id: %s", aws_account_id)
    # Extract the AWS region where this Lambda function is running.
    aws_region = os.environ["AWS_REGION"]
    LOGGER.debug("aws_region: %s", aws_region)

    # Extract source bucket name and source object key from EventBridge event.
    copy_source = aux_eventbridge_events.extract_copy_source(LOGGER, event)
    # Extract destination bucket name from environment variable.
    destination_bucket_name = os.environ.get(ENV_DATA_LAKE_DATA_BUCKET_NAME)
    # Construct destination object key based on source object key.
    destination_object_key = construct_destination_object_key(LOGGER, copy_source["Key"])

    # Copy the new call recording from the CC bucket to the DL bucket.
    # FIXME: Add some error handling here, e.g. log it somewhere specific or add to a metric.
    response = S3_CLIENT.copy_object(
        CopySource = copy_source,
        Bucket = destination_bucket_name,
        Key = destination_object_key
    )
    LOGGER.debug("response: %s", response)

# --------------------------------------------------------------------------------------------------

# Sample event
"""
{
	'version': '0',
	'id': 'd7753ed0-c2c1-f33f-4bec-bcb413086465',
	'detail-type': 'Object Created',
	'source': 'aws.s3',
	'account': '699791594599',
	'time': '2022-04-07T17:14:29Z',
	'region': 'eu-central-1',
	'resources': ['arn:aws:s3:::699791594599-eu-central-1-dev-eecc-cc-data'],
	'detail': {
		'version': '0',
		'bucket': {
			'name': '699791594599-eu-central-1-dev-eecc-cc-data'
		},
		'object': {
			'key': 'connect/699791594599-eu-central-1/CallRecordings/2022/04/07/c6ad7525-4209-4f4c-aca2-f04597dd29b3_20220407T13:14_UTC.wav',
			'size': 3925804,
			'etag': 'd74d8891bc8e594c8450a3873012ebb9',
			'sequencer': '00624F1BF4E9A2F118'
		},
		'request-id': '72G46RDDMT9EEAFR',
		'requester': '699791594599',
		'source-ip-address': '54.239.6.190',
		'reason': 'CopyObject'
	}
}
"""