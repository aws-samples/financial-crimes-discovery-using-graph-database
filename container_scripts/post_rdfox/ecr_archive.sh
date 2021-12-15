# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


export DOCKER_BUILDKIT=0
echo "ACCOUNT_ID - $ACCOUNT_ID"
echo "REGION - $REGION"

docker build -t post-rdfox .

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag post-rdfox:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/post-rdfox:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/post-rdfox:latest
