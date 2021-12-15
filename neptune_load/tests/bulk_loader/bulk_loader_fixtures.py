# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from neptune_load.sigv4_signer.sigv4_signer_test import (
    TestSigV4Signer,
    TestSignedRequest,
)
from neptune_load.bulk_loader.bulk_loader import BulkLoader, BulkloadStatus
import json
import pytest
from unittest import mock
import copy
import logging
import requests

TEST_REGION = "ap-southeast-1"
TEST_DB_ENDPOINT = f"neptune.cluster-lollollollol.{TEST_REGION}.amazonaws.com"
TEST_IAM_ROLE = "arn:aws:iam::123456789012:role/Elchfisch"
TEST_OBJECT = "s3://lalala/index.nt"
TEST_LOAD_ID = "2a0c81f7-66b5-4da3-9f7a-bb356d2ddd8b"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.fixture
def query_status_load_completed_response():
    return {
        "status": "200 OK",
        "payload": {
            "feedCount": [{"LOAD_COMPLETED": 1}],
            "overallStatus": {
                "fullUri": "s3://neptune-load-test-sev/triples.nt",
                "runNumber": 1,
                "retryNumber": 0,
                "status": "LOAD_COMPLETED",
                "totalTimeSpent": 208,
                "startTime": 1625111590,
                "totalRecords": 10895596,
                "totalDuplicates": 10895596,
                "parsingErrors": 0,
                "datatypeMismatchErrors": 0,
                "insertErrors": 0,
            },
            "errors": {
                "startIndex": 0,
                "endIndex": 0,
                "loadId": "e8653e49-89f1-404f-8764-8b24ee2d657c",
                "errorLogs": [],
            },
        },
    }


@pytest.fixture
def query_status_load_in_progress_response(query_status_load_completed_response):
    response = copy.deepcopy(query_status_load_completed_response)
    response["payload"]["overallStatus"]["status"] = "LOAD_IN_PROGRESS"
    return response


@pytest.fixture
def query_status_load_cancelled_response(query_status_load_completed_response):
    response = copy.deepcopy(query_status_load_completed_response)
    response["payload"]["overallStatus"]["status"] = "LOAD_CANCELLED_BY_USER"
    return response


@pytest.fixture
def query_status_load_in_progress_object(query_status_load_in_progress_response):
    return BulkloadStatus.create_from_api_response_text(
        json.dumps(query_status_load_in_progress_response)
    )


@pytest.fixture
def query_status_load_complete_object(query_status_load_completed_response):
    return BulkloadStatus.create_from_api_response_text(
        json.dumps(query_status_load_completed_response)
    )


@pytest.fixture
def load_initiated_success_response():
    m = mock.Mock(spec=requests.Response)
    m.status_code = 200
    m.text = json.dumps({"payload": {"loadId": TEST_LOAD_ID}})
    return m


@pytest.fixture
def successful_load_request(load_initiated_success_response):
    return TestSignedRequest(response=load_initiated_success_response)


@pytest.fixture
def valid_test_sigv4_signer(successful_load_request):
    return TestSigV4Signer(signed_request=successful_load_request)


@pytest.fixture
def valid_bulk_loader_under_test(valid_test_sigv4_signer):
    wait_between_queries_in_seconds = 0.1
    yield BulkLoader(
        iam_role_arn="arn:aws:iam::123456789012:role/Elchfisch",
        signer=valid_test_sigv4_signer,
        source=TEST_OBJECT,
        neptune_endpoint=TEST_DB_ENDPOINT,
        wait_between_queries_in_seconds=wait_between_queries_in_seconds,
        maximum_wait_in_seconds=wait_between_queries_in_seconds * 10,
    )
