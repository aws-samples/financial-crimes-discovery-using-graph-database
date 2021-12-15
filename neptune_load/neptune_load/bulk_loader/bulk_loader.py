# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from typing import Dict, overload
from requests.models import Response
from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer
import json
import time
from types import SimpleNamespace
from enum import Enum
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)


class BulkloadStatus:
    class LoadStatus(Enum):
        LOAD_NOT_STARTED = "LOAD_NOT_STARTED"
        LOAD_IN_PROGRESS = "LOAD_IN_PROGRESS"
        LOAD_COMPLETED = "LOAD_COMPLETED"
        LOAD_CANCELLED_BY_USER = "LOAD_CANCELLED_BY_USER"
        LOAD_CANCELLED_DUE_TO_ERRORS = "LOAD_CANCELLED_DUE_TO_ERRORS"
        LOAD_UNEXPECTED_ERROR = "LOAD_UNEXPECTED_ERROR"
        LOAD_FAILED = "LOAD_FAILED"
        LOAD_S3_READ_ERROR = "LOAD_S3_READ_ERROR"
        LOAD_S3_ACCESS_DENIED_ERROR = "LOAD_S3_ACCESS_DENIED_ERROR"
        LOAD_COMMITTED_W_WRITE_CONFLICTS = "LOAD_COMMITTED_W_WRITE_CONFLICTS"
        LOAD_DATA_DEADLOCK = "LOAD_DATA_DEADLOCK"
        LOAD_DATA_FAILED_DUE_TO_FEED_MODIFIED_OR_DELETED = (
            "LOAD_DATA_FAILED_DUE_TO_FEED_MODIFIED_OR_DELETED"
        )
        LOAD_FAILED_BECAUSE_DEPENDENCY_NOT_SATISFIED = (
            "LOAD_FAILED_BECAUSE_DEPENDENCY_NOT_SATISFIED"
        )
        LOAD_IN_QUEUE = "LOAD_IN_QUEUE"
        LOAD_FAILED_INVALID_REQUEST = "LOAD_FAILED_INVALID_REQUEST"

    def __init__(
        self,
        status,
        start_time,
        total_time_spent,
        total_records,
        total_duplicates,
        parsing_errors,
        insert_errors,
        source,
        raw,
    ):
        self._status = status
        self._start_time = start_time
        self._total_time_spent = total_time_spent
        self._total_records = total_records
        self._total_duplicates = total_duplicates
        self._parsing_errors = parsing_errors
        self._insert_errors = insert_errors
        self._source = source
        self._raw = raw

    @property
    def status(self):
        return self._status

    @property
    def raw(self):
        return self._raw

    @classmethod
    def create_from_api_response_text(self, api_response_text: str):
        print(api_response_text)
        return json.loads(api_response_text, cls=BulkLoadStatusDecoder)


class BulkLoadStatusDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):

        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj) -> BulkloadStatus:
        if not "payload" in obj:
            return obj
        payload = obj["payload"]
        overall_status = payload["overallStatus"]

        return BulkloadStatus(
            status=BulkloadStatus.LoadStatus(overall_status["status"]),
            start_time=overall_status["startTime"],
            total_time_spent=overall_status["totalTimeSpent"],
            total_records=overall_status["totalRecords"],
            total_duplicates=overall_status["totalDuplicates"],
            parsing_errors=overall_status["parsingErrors"],
            insert_errors=overall_status["insertErrors"],
            source=overall_status["fullUri"],
            raw=obj,
        )

    """ From https://docs.aws.amazon.com/neptune/latest/userguide/load-api-reference-status-response.html
    {
        "status" : "200 OK",
        "payload" : {
            "feedCount" : [
                {
                    "LOAD_FAILED" : number
                }
            ],
            "overallStatus" : {
                "fullUri" : "s3://bucket/key",
                "runNumber" : number,
                "retryNumber" : number,
                "status" : "string",
                "totalTimeSpent" : number,
                "startTime" : number,
                "totalRecords" : number,
                "totalDuplicates" : number,
                "parsingErrors" : number,
                "datatypeMismatchErrors" : number,
                "insertErrors" : number,
            },
            "failedFeeds" : [
                {
                    "fullUri" : "s3://bucket/key",
                    "runNumber" : number,
                    "retryNumber" : number,
                    "status" : "string",
                    "totalTimeSpent" : number,
                    "startTime" : number,
                    "totalRecords" : number,
                    "totalDuplicates" : number,
                    "parsingErrors" : number,
                    "datatypeMismatchErrors" : number,
                    "insertErrors" : number,
                }
            ],
            "errors" : {
                "startIndex" : number,
                "endIndex" : number,
                "loadId" : "string,
                "errorLogs" : [ ]
            }
        }
    }"""


class BulkLoader:
    def __init__(
        self,
        signer: SigV4Signer,
        source: str,
        neptune_endpoint: str,
        iam_role_arn: str,
        parallelism: str = "MEDIUM",
        update_single_cardinality_properties: str = "TRUE",
        queueRequest: str = "FALSE",
        region: str = "ap-southeast-1",
        source_format: str = "ntriples",
        maximum_wait_in_seconds: int = 60 * 10,
        wait_between_queries_in_seconds: int = 5,
        load_id: str = None,
    ):
        if not "s3://" in source:
            raise Exception(f"Not a valid S3 URL {source}")

        self._neptune_endpoint = neptune_endpoint
        self._signer = signer
        self._iam_role_arn = iam_role_arn
        self._parallelism = parallelism
        self._update_single_cardinality_properties = (
            update_single_cardinality_properties
        )
        self._queue_request = queueRequest
        self._region = region
        self._format = source_format
        self._source = source
        self._maximum_wait_in_seconds = maximum_wait_in_seconds
        self._wait_between_queries_in_seconds = wait_between_queries_in_seconds

        self._status: BulkloadStatus = None
        self._load_id = load_id if load_id else None

    @property
    def status(self) -> BulkloadStatus:
        if not (self._status):
            raise Exception("Not loading yet")
        return self._status

    @property
    def load_id(self) -> str:
        if not self._load_id:
            raise Exception("Not associated with a load yet")
        return self._load_id

    @load_id.setter
    def load_id(self, load_id) -> str:
        if self._load_id:
            raise Exception(f"Already bound to load {self._load_id}")
        self._load_id = load_id

    def wait_for_bulk_load_from_s3(self):
        self.initiate_bulk_load_from_s3()
        self._refresh_status()
        self._wait_for_load_complete()

    def _can_load(self):
        if self._load_id:
            raise Exception("Already bound to loadid:{self._load_id} ")

    def _wait_for_load_complete(self):
        load_complete = False
        start_time = datetime.now()
        while not load_complete:
            time.sleep(self._wait_between_queries_in_seconds)
            logger.info(self.status.raw)
            if self.status.status == BulkloadStatus.LoadStatus.LOAD_COMPLETED:
                load_complete = True
            time_waiting = datetime.now() - start_time
            if time_waiting.seconds >= self._maximum_wait_in_seconds:
                raise Exception(
                    f"Load did not complete within {self._maximum_wait_in_seconds} seconds"
                )
            self._refresh_status()

    def _refresh_status(self):
        self.load_id
        query_string = json.dumps(self._construct_status_query())

        signed_request = self._signer.get_signed_request(
            host=self._neptune_endpoint,
            method="GET",
            query_type="loader",
            query=query_string,
        )

        response_text: Response = self._execute_and_handle_signed_request(
            signed_request=signed_request
        )

        self._status = BulkloadStatus.create_from_api_response_text(response_text)
        return

    def _construct_status_query(self):
        return {
            "loadId": self.load_id,
            "details": "true",
            "errors": "true",
            "page": "1",
        }

    def initiate_bulk_load_from_s3(
        self,
    ):
        logger.info(f"Bulk load requested")
        query_string = json.dumps(self._construct_load_query())

        signed_request = self._signer.get_signed_request(
            host=self._neptune_endpoint,
            method="POST",
            query_type="loader",
            query=query_string,
        )
        response = self._execute_and_handle_signed_request(
            signed_request=signed_request
        )

        self.load_id = json.loads(response)["payload"]["loadId"]
        self._refresh_status()
        logger.info(f"Bulk load request succeeded {self.load_id} {self.status.status}")

    def _execute_and_handle_signed_request(self, signed_request) -> SimpleNamespace:

        response: Response = signed_request.execute()
        if not (response.status_code == 200):
            raise Exception(f"Request returned {response.status_code} {response.text}")

        return response.text

    def cancel_load(self):
        query_string = json.dumps(self._construct_cancel_query())
        logger.info(f"Cancellation for {self.load_id} requested")
        signed_request = self._signer.get_signed_request(
            host=self._neptune_endpoint,
            method="DELETE",
            query_type="loader",
            query=query_string,
        )
        response = self._execute_and_handle_signed_request(
            signed_request=signed_request
        )
        self._refresh_status()
        logger.info(f"Cancellation for {self.load_id} successful")

    def reset_database(self):
        token = self.get_reset_token()
        reset_response = self.perform_reset(reset_token=token)

        return reset_response

    def get_reset_token(self):
        reset_token_request_string = json.dumps(self._construct_reset_token_query())
        logger.info(f"Reset token requested")

        signed_reset_request = self._signer.get_signed_request(
            host=self._neptune_endpoint,
            method="POST",
            query_type="system",
            query=reset_token_request_string,
        )
        response = self._execute_and_handle_signed_request(
            signed_request=signed_reset_request
        )
        token = json.loads(response)["payload"]["token"]
        logger.debug(f"Reset token is {token}")
        return token

    def perform_reset(self, reset_token):
        reset_request_string = json.dumps(self._construct_reset_query(reset_token))
        logger.warn(f"Reset token requested")
        signed_reset_request = self._signer.get_signed_request(
            host=self._neptune_endpoint,
            method="POST",
            query_type="system",
            query=reset_request_string,
        )
        response = self._execute_and_handle_signed_request(
            signed_request=signed_reset_request
        )
        return response

    def get_active_loads(self):
        query_string = json.dumps(self._construct_detail_query())
        signed_request = self._signer.get_signed_request(
            host=self._neptune_endpoint,
            method="GET",
            query_type="loader",
            query=query_string,
        )

        response_text: Response = self._execute_and_handle_signed_request(
            signed_request=signed_request
        )

        load_object = json.loads(response_text)
        return load_object["payload"]["loadIds"]

    def _construct_detail_query(self) -> Dict:
        detail_query = {"details": "TRUE"}
        return detail_query

    def _construct_cancel_query(self) -> Dict:
        cancel_query = {"loadId": self.load_id}
        return cancel_query

    def _construct_load_query(self) -> Dict:
        load_query = {
            "source": self._source,
            "format": self._format,
            "iamRoleArn": self._iam_role_arn,
            "region": self._region,
            "failOnError": "FALSE",
            "parallelism": self._parallelism,
            "updateSingleCardinalityProperties": self._update_single_cardinality_properties,
            "queueRequest": self._queue_request,
        }

        return load_query

    def _construct_reset_token_query(self) -> Dict:
        reset_query = {
            "action": "initiateDatabaseReset",
        }

        return reset_query

    def _construct_reset_query(self, reset_token) -> Dict:
        reset_query = {
            "action": "performDatabaseReset",
            "token": reset_token,
        }

        return reset_query
