from enum import Enum, auto
import logging
import json

# ---------------------------------------------------------------------------------------------------------------------
# Globals.
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# Lambda event source enumeration.
# ---------------------------------------------------------------------------------------------------------------------

class LambdaEventSource(Enum):
    API = auto()
    SNS = auto()
    SQS = auto()

# ---------------------------------------------------------------------------------------------------------------------
# An abstraction of a Lambda event that contains SNS messages with embedded S3 events.
# ---------------------------------------------------------------------------------------------------------------------

class SnsMessagesWithEmbeddedS3Events:

    def __init__(self, logger, lambda_event):
        self.logger = logger
        self.lambda_event = lambda_event
        # We expect SNS messages coming in a "Records" array. Not sure if there will ever be more than one record.
        self.sns_messages = lambda_event["Records"]

    def log(self):
        self.logger.debug("Full lambda event: %s", self.lambda_event)
        self.logger.debug("Number of SNS messages: %d", self.get_sns_message_count())

    # Retrieve amount of SNS messages in the Lambda event (probably it's 1).
    def get_sns_message_count(self):
        return len(self.sns_messages)

    # Retrieve all S3 events from all SNS messages.
    def get_all_s3_events(self):
        self.logger.debug("Extracting all S3 events from all SNS messages.")
        i = 0; j = 0
        s3_events = []
        # Within each SNS message record, there's an object "Sns". Within that object:
        # - The message body is in the "Message" object.
        # - Message meta data is in the "MessageAttributes" object.
        # Not sure if there will ever be more than one record in this array, but let's be prepared for it.
        for sns_record in self.sns_messages:
            i += 1
            self.logger.debug("Inspecting SNS message #%d.", i)
            #message_meta = json.loads(sns_record["Sns"]["MessageAttributes"])
            message_meta = sns_record["Sns"]["MessageAttributes"]
            self.logger.debug("Message attributes: %s", message_meta)
            message_body = json.loads(sns_record["Sns"]["Message"])
            self.logger.debug("Message body: %s", message_body)
            # Now, every message body again has a "Records" array where each item is a single S3 event.
            # Not sure if there will ever be more than a single S3 event, but let's be prepared for it.
            for s3_record in message_body["Records"]:
                j += 1
                self.logger.debug("Fetching S3 event #%d.", j)
                s3_events.append(SingleS3Event(self.logger, self.lambda_event, s3_record))
        return s3_events

# ---------------------------------------------------------------------------------------------------------------------
# An abstraction of a single S3 event taken somewhere out of a Lambda event.
# ---------------------------------------------------------------------------------------------------------------------

class SingleS3Event:

    def __init__(self, logger, event, deserialized_single_s3_event):
        self.logger = logger
        self.event = event
        #self.single_s3_event = json.loads(serialized_single_s3_event)
        self.single_s3_event = deserialized_single_s3_event
        self.log()

    def log(self):
        self.logger.debug("single_s3_event: %s", self.single_s3_event)

    def get_single_s3_event(self):
        return self.single_s3_event

    def is_event_source_s3(self):
        if "eventSource" in self.single_s3_event:
            return self.single_s3_event["eventSource"] == "aws:s3"
        return False

    def is_object_created_put(self):
        if "eventName" in self.single_s3_event:
            return self.single_s3_event["eventName"] == "ObjectCreated:Put"
        return False

    def get_bucket_name(self):
        return self.single_s3_event["s3"]["bucket"]["name"]

    def get_bucket_arn(self):
        return self.single_s3_event["s3"]["bucket"]["arn"]

    def get_object_key(self):
        return self.single_s3_event["s3"]["object"]["key"]

# ---------------------------------------------------------------------------------------------------------------------
