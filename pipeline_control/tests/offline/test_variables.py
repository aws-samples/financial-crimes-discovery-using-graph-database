# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pytest

TEST_KEY = "2021-07-01"
TEST_FROZE_DATE = "2021-07-01"
TEST_JOB_ID = f"{TEST_KEY}_{TEST_FROZE_DATE}_000"
DERIVED_JOB_ID = TEST_JOB_ID
TEST_CLUSTER_NAME = "glumanda-cluster"
JOBSPEC_NAME = "some.rdfoxjob.json"
TEST_RDFOX_LOG_FILE_NAME = "rdfox.log"
TEST_JOBSPEC_KEY = f"{TEST_KEY}/{JOBSPEC_NAME}"
TEST_RESULT_DATA_KEY = f"some/stuff/doesntmatter/{TEST_JOB_ID}"
TEST_RESULT_KEY = f"{TEST_RESULT_DATA_KEY}/{TEST_RDFOX_LOG_FILE_NAME}"
TEST_INFERENCE_STATS_KEY = "rdfox.log"
TEST_BUCKET_NAME = "the-name-is-the-name"
TEST_RESULT_BUCKET_NAME = "the-name-was-the-name"
TEST_SOURCE_FORMAT = "rdfxml"
TEST_REGION = "ap-southeast-1"
TEST_NEPTUNE_ENDPOINT = f"neptune.cluster-lollollollol.{TEST_REGION}.amazonaws.com"
TEST_IAM_ROLE = "arn:aws:iam::123456789012:role/Elchfisch"
TEST_OBJECT = "s3://lalala/index.nt"
TEST_NEPTUNE_LOAD_ID = "2a0c81f7-66b5-4da3-9f7a-bb356d2ddd8b"
TEST_FROZE_DATE = "2021-07-01"
TEST_KUBERNETES_NAME = "rdfox-adasdasd"
TEST_NUMBER_OF_CORES = 4
TEST_AUTO_SHUTDOWN = False
TEST_NEPTUNE_WRITER_INSTANCE = "m5d.12xlarge"
TEST_NOTIFICATION_TOPIC = "SNSStack-EmailSNSTopic-XYZ"
TEST_WORKER_NODE_TYPE = "x1e.32xlarge"


def pytest_configure():
    pytest.TEST_KEY = TEST_KEY
    pytest.TEST_FROZE_DATE = TEST_FROZE_DATE
    pytest.TEST_CLUSTER_NAME = TEST_CLUSTER_NAME
    pytest.JOBSPEC_NAME = JOBSPEC_NAME
    pytest.TEST_BUCKET_NAME = TEST_BUCKET_NAME
    pytest.DERIVED_JOB_ID = TEST_JOB_ID
    pytest.TEST_REGION = TEST_REGION
    pytest.TEST_NEPTUNE_ENDPOINT = TEST_NEPTUNE_ENDPOINT
    pytest.TEST_IAM_ROLE = TEST_IAM_ROLE
    pytest.TEST_OBJECT = "s3://lalala/index.nt"
    pytest.TEST_NEPTUNE_LOAD_ID = TEST_NEPTUNE_LOAD_ID
    pytest.TEST_JOBSPEC_KEY = f"{TEST_KEY}/{JOBSPEC_NAME}"
    pytest.TEST_CLUSTER_NAME = TEST_CLUSTER_NAME
    pytest.TEST_RESULT_BUCKET = TEST_RESULT_BUCKET_NAME
    pytest.TEST_RESULT_KEY = TEST_RESULT_KEY
    pytest.TEST_JOB_ID = TEST_JOB_ID
    pytest.TEST_RESULT_LOAD_SOURCE = f"s3://{TEST_RESULT_BUCKET_NAME}/{TEST_RESULT_KEY}"
    pytest.TEST_INFERENCE_STATS_KEY = TEST_INFERENCE_STATS_KEY
    pytest.TEST_KUBERNETES_NAME = TEST_KUBERNETES_NAME
    pytest.TEST_NUMBER_OF_CORES = TEST_NUMBER_OF_CORES
    pytest.TEST_AUTO_SHUTDOWN = TEST_AUTO_SHUTDOWN
    pytest.TEST_SOURCE_FORMAT = TEST_SOURCE_FORMAT
    pytest.TEST_RDFOXLOG_FILE_NAME = TEST_RDFOX_LOG_FILE_NAME
    pytest.TEST_RESULT_DATA_KEY = TEST_RESULT_DATA_KEY
    pytest.TEST_NEPTUNE_WRITER_INSTANCE = TEST_NEPTUNE_WRITER_INSTANCE
    pytest.TEST_NOTIFICATION_TOPIC = TEST_NOTIFICATION_TOPIC
    pytest.TEST_WORKER_NODE_TYPE = TEST_WORKER_NODE_TYPE
