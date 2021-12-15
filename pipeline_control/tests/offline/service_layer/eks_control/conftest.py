# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


import boto3
import moto
import pytest

TEST_CLUSTER_NAME = "glumanda-cluster"
TEST_ROLE_ARN = "arn:aws:iam::123456789012:role/EKS"
