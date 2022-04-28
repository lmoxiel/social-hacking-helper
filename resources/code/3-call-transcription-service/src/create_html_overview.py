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

S3_CLIENT = boto3.client("s3")

ENV_DATA_LAKE_DATA_BUCKET_ARN  = "DATA_LAKE_DATA_BUCKET_ARN"
ENV_DATA_LAKE_DATA_BUCKET_NAME = "DATA_LAKE_DATA_BUCKET_NAME"

# --------------------------------------------------------------------------------------------------
# Create a table in HTML as a nice overview of the call analytics results.
# --------------------------------------------------------------------------------------------------

def construct_destination_object_key(logger, source_object_key):
    """
    Determine the destination object key based on the source object key.
    """
    logger.debug("Create the destination object key, based on the source object key:")
    logger.debug("source_object_key: %s", source_object_key)
    destination_object_key = source_object_key
    # Replace "raw" with "prepared".
    destination_object_key = destination_object_key.replace("/raw/", "/prepared/")
    # Replace ".json" with ".html"
    destination_object_key = destination_object_key.replace(".json", ".html")
    logger.debug("destination_object_key: %s", destination_object_key)
    return destination_object_key


def load_raw_call_analytics(source_bucket_name, source_object_key):
    LOGGER.debug("Read S3 object and make it a JSON object.")
    response = S3_CLIENT.get_object(
        Bucket = source_bucket_name,
        Key    = source_object_key
    )
    LOGGER.debug("response: %s", response)
    object_body = response['Body']
    LOGGER.debug("object_body: %s", object_body)
    full_text = object_body.read()
    LOGGER.debug("full_text: %s", full_text)
    raw_call_analytics = json.loads(full_text)
    # Store the object key of the source data.
    # We can use it as input for the object key of the target data later.
    raw_call_analytics['source_object_key'] = source_object_key
    LOGGER.debug("raw_call_analytics: %s", raw_call_analytics)
    return raw_call_analytics


def create_html_overview(raw_call_analytics):
    #LOGGER.debug("raw_call_analytics: %s", raw_call_analytics)
    html_output = ""
    html_output += "<html>\n"
    html_output += "  <head>\n"
    html_output += "  </head>\n"
    html_output += "  <body>\n"
    html_output += "    <table class='NiceTable' style='border: 1px solid black;'>\n"
    html_output += "      <colgroup>\n"
    html_output += "        <col span='1' style='width:15%'>\n"
    html_output += "        <col span='1' style='width:15%'>\n"
    html_output += "        <col span='1' style='width:70%'>\n"
    html_output += "      </colgroup>\n"
    html_output += "      <tr class='NiceTable' style='background-color:#ff9900;line-height:200%'>\n"
    html_output += "        <th class='NiceTable' style='border: 1px solid black;text-align:left'>\n"
    html_output += "          Speaker\n"
    html_output += "        </th>\n"
    html_output += "        <th class='NiceTable' style='border: 1px solid black;text-align:left'>\n"
    html_output += "          Sentiment\n"
    html_output += "        </th>\n"
    html_output += "        <th class='NiceTable' style='border: 1px solid black;text-align:left'>\n"
    html_output += "          Content\n"
    html_output += "        </th>\n"
    html_output += "      </tr>\n"
    for transcript_line in raw_call_analytics['Transcript']:
        participant_role = transcript_line['ParticipantRole']
        if (participant_role == 'CUSTOMER'):
            html_output += "      <tr class='NiceTable' style='vertical-align:top;background-color:lightgray'>\n"
        else:
            html_output += "      <tr class='NiceTable' style='vertical-align:top'>\n"
        html_output += "        <td class='NiceTable' style='border: 1px solid black;'>\n"
        html_output += "          " + participant_role + "\n"
        html_output += "        </td>\n"
        line_sentiment = transcript_line['Sentiment']
        LOGGER.debug("line_sentiment: %s", line_sentiment)
        if (line_sentiment == 'NEGATIVE'):
            html_output += "        <td class='NiceTable' style='border: 1px solid black;color:red'>\n"
        elif (line_sentiment == 'NEUTRAL'):
            html_output += "        <td class='NiceTable' style='border: 1px solid black;color:orange'>\n"
        elif (line_sentiment == 'POSITIVE'):
            html_output += "        <td class='NiceTable' style='border: 1px solid black;color:green'>\n"
        else:
            html_output += "        <td class='NiceTable' style='border: 1px solid black;'>\n"
        html_output += "          " + line_sentiment + "\n"
        html_output += "        </td>\n"
        html_output += "        <td class='NiceTable' style='border: 1px solid black;'>\n"
        html_output += "          " + transcript_line['Content'] + "\n"
        html_output += "        </td>\n"
        html_output += "      </tr>\n"
    html_output += "    </table>\n"
    html_output += "  </body>\n"
    html_output += "</html>\n"
    LOGGER.debug("html_output: %s", html_output)
    return html_output

def write_html_overview(html_output, destination_bucket_name, destination_object_key):
    LOGGER.debug("Save HTML overview in S3.")
    response = S3_CLIENT.put_object(
        Body        = html_output,
        Bucket      = destination_bucket_name,
        ContentType = "text/html",
        Key         = destination_object_key,
    )
    LOGGER.debug("response: %s", response)

# --------------------------------------------------------------------------------------------------
# Lambda handler.
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

    # Load the source object as JSON.
    raw_call_analytics = load_raw_call_analytics(source_bucket_name, source_object_key)
    # Create the HTML table.
    html_output = create_html_overview(raw_call_analytics)
    # Write HTML output into new S3 object.
    write_html_overview(html_output, destination_bucket_name, destination_object_key)

# --------------------------------------------------------------------------------------------------
