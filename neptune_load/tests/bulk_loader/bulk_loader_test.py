# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from datetime import datetime
from types import SimpleNamespace
from neptune_load.bulk_loader.bulk_loader import BulkloadStatus
import json
from pyexpect import expect
import pytest
from unittest import mock
import logging

from requests.models import Response

TEST_REGION = "ap-southeast-1"
TEST_DB_ENDPOINT = f"neptune.cluster-lollollollol.{TEST_REGION}.amazonaws.com"
TEST_IAM_ROLE = "arn:aws:iam::123456789012:role/Elchfisch"
TEST_OBJECT = "s3://lalala/index.nt"
TEST_LOAD_ID = "2a0c81f7-66b5-4da3-9f7a-bb356d2ddd8b"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BulkloadQueryMock:
    def __init__(
        self,
        while_waiting,
        when_done,
        max_iterations,
        max_seconds=0,
    ):
        self._while_waiting = while_waiting
        self._when_done = when_done
        self._iterations = max_iterations - 1
        self._current_iteration = 0
        self._max_seconds = max_seconds
        self._start_time = None

    def serve(self):
        duration = 0
        if not self._start_time and self._max_seconds:
            self._start_time = datetime.now()
        if self._start_time:
            duration = (datetime.now() - self._start_time).seconds
        if self._current_iteration >= self._iterations or duration >= self._max_seconds:
            return self._when_done
        else:
            self._current_iteration = self._current_iteration + 1
            return self._while_waiting


class Test_1_Bulkloadstatus:
    def test_create_from_api_response_text(
        self, query_status_load_in_progress_response
    ):
        bulk_load_status = BulkloadStatus.create_from_api_response_text(
            json.dumps(query_status_load_in_progress_response)
        )
        expect(type(bulk_load_status)).to.equals(BulkloadStatus)


class Test_2_BulkLoader:
    def test_1_initiate_bulk_load_from_s3(
        self,
        valid_bulk_loader_under_test,
        query_status_load_in_progress_response,
        load_initiated_success_response,
    ):
        with mock.patch(
            "neptune_load.bulk_loader.bulk_loader.BulkLoader._execute_and_handle_signed_request"
        ) as eahsr:
            eahsr.side_effect = [
                load_initiated_success_response.text,
                json.dumps(query_status_load_in_progress_response),
            ]
            valid_bulk_loader_under_test.initiate_bulk_load_from_s3()
            expect(valid_bulk_loader_under_test.load_id).to.equal(TEST_LOAD_ID)

    @mock.patch(
        "neptune_load.bulk_loader.bulk_loader.BulkloadStatus.create_from_api_response_text"
    )
    def test_wait_for_bulk_load_from_s3(
        self,
        mock_bls,
        valid_bulk_loader_under_test,
        query_status_load_complete_object,
        query_status_load_in_progress_object,
    ):
        success_in_ten = BulkloadQueryMock(
            when_done=query_status_load_complete_object,
            while_waiting=query_status_load_in_progress_object,
            max_iterations=3,
        )

        mock_bls.side_effect = lambda x: success_in_ten.serve()

        valid_bulk_loader_under_test.wait_for_bulk_load_from_s3()
        expect(valid_bulk_loader_under_test.load_id).to.equal(TEST_LOAD_ID)
        expect(valid_bulk_loader_under_test.status.status).to.equal(
            BulkloadStatus.LoadStatus.LOAD_COMPLETED
        )

    def test_3_cancel_bulk_load(
        self,
        valid_bulk_loader_under_test,
        load_initiated_success_response,
        query_status_load_in_progress_response,
        query_status_load_cancelled_response,
    ):
        with mock.patch(
            "neptune_load.bulk_loader.bulk_loader.BulkLoader._execute_and_handle_signed_request"
        ) as eahsr:
            eahsr.side_effect = [
                load_initiated_success_response.text,
                json.dumps(query_status_load_in_progress_response),
                json.dumps(query_status_load_in_progress_response),
                json.dumps(query_status_load_cancelled_response),
            ]
            valid_bulk_loader_under_test.initiate_bulk_load_from_s3()
            valid_bulk_loader_under_test.cancel_load()
            expect(valid_bulk_loader_under_test.status.status).equals(
                BulkloadStatus.LoadStatus.LOAD_CANCELLED_BY_USER
            )
