from operator import truediv
import os
import logging
import json
import datetime
import uuid
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

TRANSCRIBE_CLIENT = boto3.client("transcribe")

ENV_DATA_LAKE_DATA_BUCKET_ARN  = "DATA_LAKE_DATA_BUCKET_ARN"
ENV_DATA_LAKE_DATA_BUCKET_NAME = "DATA_LAKE_DATA_BUCKET_NAME"
ENV_DATA_ACCESS_ROLE_ARN = "DATA_ACCESS_ROLE_ARN"

# --------------------------------------------------------------------------------------------------
# Functions.
# --------------------------------------------------------------------------------------------------

def construct_destination_object_key(logger, source_object_key):
    """
    Based on the object key of the newly ingested Amazon Connect call recording, construct the
    object key for the output of the call analytics job in Amazon Transcribe.
    """
    logger.debug("Create the destination object key, based on the source object key:")
    destination_object_key = source_object_key.replace(
        aux_paths.PATH_CONNECT_CALLRECORDINGS_RAW, aux_paths.PATH_TRANSCRIBE_CALLANALYTICS_RAW
    )
    logger.debug("destination_object_key: %s", destination_object_key)
    destination_object_key = destination_object_key.replace(
        ".wav", aux_paths.PATH_CALL_ANALYTICS_RESULT + ".json"
    )
    logger.debug("destination_object_key: %s", destination_object_key)
    return destination_object_key


def run_call_analytics(logger, source_bucket_name, source_object_key, destination_bucket_name, destination_object_key):
    logger.debug("Run call analytics with Amazon Transcribe.")
    # The resulting S3 URI of the media object.
    media_uri = "s3://" + source_bucket_name + "/" + source_object_key
    logger.debug("S3 URI for the media object: %s", media_uri)
    # Assemble output location.
    output_location = "s3://" + destination_bucket_name + "/" + destination_object_key
    logger.debug("output_location: %s", output_location)

    # Transcribe job name.
    # FIXME: Extract the last segment of the source object key or something to have a reasonable job name.
    job_name = "job-" + uuid.uuid4().hex
    logger.debug("job_name: %s", job_name)

    logger.debug("ENV_DATA_ACCESS_ROLE_ARN: %s", os.environ.get(ENV_DATA_ACCESS_ROLE_ARN))

    # Invoke Transcribe-API.
    response = TRANSCRIBE_CLIENT.start_call_analytics_job(
        CallAnalyticsJobName   = job_name,
        Media                  = {"MediaFileUri": media_uri},
        OutputLocation         = output_location,
        DataAccessRoleArn      = os.environ.get(ENV_DATA_ACCESS_ROLE_ARN),
        ChannelDefinitions     = [
            {'ChannelId': 0, 'ParticipantRole': 'CUSTOMER'},
            {'ChannelId': 1, 'ParticipantRole': 'AGENT'}
        ]
    )
    logger.debug("response: %s", response)

# --------------------------------------------------------------------------------------------------
# # Lambda handler.
# --------------------------------------------------------------------------------------------------

def lambda_handler(event, context):

    # If the environment advises on a specific debug level, set it accordingly.
    aux.update_log_level(LOGGER, event, context)
    # Log environment details.
    aux.log_env_details(LOGGER)
    # Log request details.
    aux.log_event_and_context(LOGGER, event, context)

    source_bucket_name = aux_eventbridge_events.extract_source_bucket_name(LOGGER, event)
    source_object_key = aux_eventbridge_events.extract_source_object_key(LOGGER, event)
    # Extract destination bucket name from environment variable.
    destination_bucket_name = os.environ.get(ENV_DATA_LAKE_DATA_BUCKET_NAME)
    # Construct destination object key based on source object key.
    destination_object_key = construct_destination_object_key(LOGGER, source_object_key)

    # Let's go!
    run_call_analytics(LOGGER, source_bucket_name, source_object_key, destination_bucket_name, destination_object_key)

# --------------------------------------------------------------------------------------------------

# Sample event
"""
{
	'version': '0',
	'id': 'c3ae46a1-ef0c-8788-7e61-b07928a9404b',
	'detail-type': 'Object Created',
	'source': 'aws.s3',
	'account': '699791594599',
	'time': '2022-04-08T12:08:15Z',
	'region': 'eu-central-1',
	'resources': ['arn:aws:s3:::699791594599-eu-central-1-dev-eecc-dl-raw-data'],
	'detail': {
		'version': '0',
		'bucket': {
			'name': '699791594599-eu-central-1-dev-eecc-dl-raw-data'
		},
		'object': {
			'key': 'contact-center/call-recordings/raw-audio-from-connect/2022/04/07/c6ad7525-4209-4f4c-aca2-f04597dd29b3_2022-04-07T20:02:00Z.wav',
			'size': 3925804,
			'etag': 'a98ab103cfaf9c17f7d99b0c7c948239',
			'sequencer': '00625025AF96AAC698'
		},
		'request-id': 'H01FV5YAMSN7YFSY',
		'requester': '699791594599',
		'source-ip-address': '3.68.105.196',
		'reason': 'CopyObject'
	}
}
"""
