#!/bin/bash

echo "--------------------------------------------------------------------------------"
echo "Deploying Speech AI workshop services"
echo "--------------------------------------------------------------------------------"

# Prepare AWS account details.
echo "--------------------------------------------------------------------------------"
echo "Fetching AWS account details"
echo "--------------------------------------------------------------------------------"
source "./my-aws-account-details.sh"
echo "AWS account details:"
echo "SAM_AWS_ACCOUNT_ID = "$SAM_AWS_ACCOUNT_ID
echo "SAM_AWS_REGION     = "$SAM_AWS_REGION
echo "SAM_AWS_PROFILE    = "$SAM_AWS_PROFILE
echo "SAM_STAGE          = "$SAM_STAGE
echo "SAM_BUCKET_NAME    = "$SAM_BUCKET_NAME

# Prepare environment variables.
## AWS account details.
# export SAM_AWS_ACCOUNT_ID=669759248652
# export SAM_AWS_REGION=eu-central-1
# export SAM_AWS_PROFILE=burner1
# export SAM_STAGE=dev
# export SAM_BUCKET_NAME=$SAM_AWS_ACCOUNT_ID-$SAM_AWS_REGION-sam-cli-source-bucket

# Create artifact bucket for SAM.
aws s3 mb s3://$SAM_BUCKET_NAME --profile $SAM_AWS_PROFILE --region $SAM_AWS_REGION

# Prepare workload details.
export SAM_WORKLOAD=eecc
export SAM_WORKLOAD_LONG=elvish-electrons-customer-care
echo "Workload details:"
echo "SAM_WORKLOAD       = "$SAM_WORKLOAD
echo "SAM_WORKLOAD_LONG  = "$SAM_WORKLOAD_LONG

# FIXME: For all stages beyond DEV, we need to override some CloudFormation template parameters!

# Execute deploy.sh for each service context.
echo "--------------------------------------------------------------------------------"
echo "Deploying service 0-account-preparation"
echo "--------------------------------------------------------------------------------"
cd "0-account-preparation"
source "./deploy.sh"
cd ../

echo "--------------------------------------------------------------------------------"
echo "Deploying service 1-application-preparation"
echo "--------------------------------------------------------------------------------"
cd "1-application-preparation"
source "./deploy.sh"
cd ../

echo "--------------------------------------------------------------------------------"
echo "Deploying service 2-datalake-ingestion-service"
echo "--------------------------------------------------------------------------------"
cd "2-datalake-ingestion-service"
source "./deploy.sh"
cd ../

echo "--------------------------------------------------------------------------------"
echo "Deploying service 3-call-transcription-service"
echo "--------------------------------------------------------------------------------"
cd "3-call-transcription-service"
source "./deploy.sh"
cd ../

echo "--------------------------------------------------------------------------------"
echo "Deploying service 4-call-comprehension-service"
echo "--------------------------------------------------------------------------------"
cd "4-call-comprehension-service"
source "./deploy.sh"
cd ../

# Done.
echo "--------------------------------------------------------------------------------"
echo "All done"
echo "--------------------------------------------------------------------------------"
