# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


export DOCKER_BUILDKIT=0
echo "ACCOUNT_ID - $ACCOUNT_ID"
echo "REGION - $REGION"

BUCKET_NAME="data-store"
DATA_PATH="10M1DAY"
echo "Using bucket - $BUCKET_NAME"
cp -r ../../transactions_generator transactions_generator
docker build -t data-generator --build-arg ARG_BUCKET_NAME=$BUCKET_NAME  --build-arg ARG_THREAD_COUNT=20 --build-arg ARG_NUM_OF_MSG=5000 --build-arg ARG_NUM_OF_FILES=10 --no-cache .
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag data-generator:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/data-generator:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/data-generator:latest
rm -r transactions_generator