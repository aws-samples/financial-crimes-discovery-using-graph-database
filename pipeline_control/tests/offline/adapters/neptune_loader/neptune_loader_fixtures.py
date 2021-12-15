# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from unittest.mock import patch

import moto
import pytest
from neptune_load.bulk_loader.bulk_loader import BulkloadStatus

from pipeline_control.adapters.neptune_loader.neptune_loader import NeptuneLoader


# From https://docs.aws.amazon.com/neptune/latest/userguide/load-api-reference-status-response.html
@pytest.fixture
def load_success_text():
    return {
        "status": "200 OK",
        "payload": {
            "feedCount": [{"LOAD_FAILED": 0}],
            "overallStatus": {
                "fullUri": pytest.TEST_RESULT_LOAD_SOURCE,
                "runNumber": 1,
                "retryNumber": 0,
                "status": "LOAD_COMPLETED",
                "totalTimeSpent": 10,
                "startTime": 1,
                "totalRecords": 100,
                "totalDuplicates": 0,
                "parsingErrors": 0,
                "datatypeMismatchErrors": 0,
                "insertErrors": 0,
            },
            "failedFeeds": [],
            "errors": {
                "startIndex": 0,
                "endIndex": 0,
                "loadId": pytest.TEST_NEPTUNE_LOAD_ID,
                "errorLogs": [],
            },
        },
    }


@pytest.fixture
@moto.mock_sts
def neptune_loader_under_test(g_job_configurations_neptune_configuration):
    return NeptuneLoader(
        signer=None,
        neptune_load_configuration=g_job_configurations_neptune_configuration,
    )


def set_test_load_id(*args, **kwargs):
    args[0].load_id = pytest.TEST_NEPTUNE_LOAD_ID


@pytest.fixture
def set_status_success(load_success_text):
    def closure(*args, **kwargs):
        self = args[0]
        self._status = BulkloadStatus.create_from_api_response_text(
            json.dumps(load_success_text)
        )

    yield closure


@pytest.fixture
def mocked_bulk_loader(set_status_success):
    with patch(
        "neptune_load.bulk_loader.bulk_loader.BulkLoader._refresh_status",
        autospec=True,
        side_effect=set_status_success,
    ) as mock_refresh:
        with patch(
            "neptune_load.bulk_loader.bulk_loader.BulkLoader.initiate_bulk_load_from_s3",
            autospec=True,
            side_effect=set_test_load_id,
        ) as mock_load:
            yield (mock_refresh, mock_load)
