#!/bin/bash

# -----------------------------------------------------------------------------
# Copy this file to "my-aws-account-details.sh" and fill in the values for your
# prepared AWS account below.
# -----------------------------------------------------------------------------

# Prepare environment variables.
## AWS account details.
export SAM_AWS_ACCOUNT_ID=<your-aws-account-id>
export SAM_AWS_REGION=<the-aws-region-you-want-to-use>
export SAM_AWS_PROFILE=<the-profile-name-in-your-credentials-file>
export SAM_STAGE=dev
export SAM_BUCKET_NAME=$SAM_AWS_ACCOUNT_ID-$SAM_AWS_REGION-sam-cli-source-bucket
