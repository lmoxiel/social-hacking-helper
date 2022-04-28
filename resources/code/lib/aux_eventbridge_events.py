import json
import logging

# --------------------------------------------------------------------------------------------------
# Globals.
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Functions.
# --------------------------------------------------------------------------------------------------

def is_relevant_event_object_key(logger, event, relevant_object_key_segment):
    """
    Check if an object key in an EventBridge event is relevant, i.e. it contains a certain path
    segment. This function should usually not be necessary as the EventBridge pattern should already
    take care of this.
    """
    logger.debug("Check if the EventBridge event is about a relevant object key.")
    object_key = event["detail"]["object"]["key"]
    if relevant_object_key_segment in object_key:
        logger.debug("EventBridge event is relevant.")
        return True
    logger.debug("EventBridge event is not relevant.")
    return False

# --------------------------------------------------------------------------------------------------

def extract_source_bucket_name(logger, event):
    """
    Just get the bucket name of the referred S3 object out of the EventBridge event.
    """
    source_bucket_name = event["detail"]["bucket"]["name"]
    logger.debug("source_bucket_name: %s", source_bucket_name)
    return source_bucket_name

def extract_source_object_key(logger, event):
    """
    Just get the object key of the referred S3 object out of the EventBridge event.
    """
    source_object_key = event["detail"]["object"]["key"]
    logger.debug("source_object_key: %s", source_object_key)
    return source_object_key

def extract_copy_source(logger, event):
    """
    For an upcoming S3 copy object operation, extract the source bucket name and the source object
    key from an EventBridge S3 event.
    """
    source_bucket_name = extract_source_bucket_name(logger, event)
    source_object_key = extract_source_object_key(logger, event)

    logger.debug("source_bucket_name: %s", source_bucket_name)
    logger.debug("source_object_key: %s", source_object_key)

    copy_source = {"Bucket": source_bucket_name, "Key": source_object_key}
    logger.debug("copy_source: %s", json.dumps(copy_source, indent=4))

    return copy_source
