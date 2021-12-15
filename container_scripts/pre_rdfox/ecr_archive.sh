# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


export DOCKER_BUILDKIT=0
echo "ACCOUNT_ID - $ACCOUNT_ID"
echo "REGION - $REGION"

docker build -t pre-rdfox .

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag pre-rdfox:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/pre-rdfox:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/pre-rdfox:latest
