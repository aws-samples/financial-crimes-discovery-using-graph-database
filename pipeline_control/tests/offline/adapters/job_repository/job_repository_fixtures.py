# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from datetime import datetime

import moto
import pytest
from freezegun import freeze_time

from pipeline_control.adapters.job_repository.ddb_model import DDBJob
from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStats,
)
from pipeline_control.domain.model import Job, JobStatus
from tests.offline.test_variables import TEST_FROZE_DATE


@pytest.fixture
def test_ddb_job():
    with freeze_time(pytest.TEST_FROZE_DATE):
        try:
            yield DDBJob(
                pk=pytest.TEST_KEY,
                sk=f"{TEST_FROZE_DATE}#000",
                key=pytest.TEST_KEY,
                job_id=pytest.TEST_JOB_ID,
                job_configuration=RDFoxJobConfiguration().json,
                neptune_load_id=pytest.TEST_NEPTUNE_LOAD_ID,
                job_created=datetime.now(),
                job_updated=datetime.now(),
                job_status=repr(JobStatus.SCHEDULED),
                rdfox_statistics=InferenceStats().json,
                rdfox_statistics_raw="""INFERENCETIME-13-Jul-2021 10:28:28|13-Jul-2021 10:28:40
        LOADTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:28
        TOTALTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:40""",
                neptune_statistics_raw={
                    "status": "200 OK",
                    "payload": {
                        "feedCount": [{"LOAD_FAILED": 0}],
                        "overallStatus": {
                            "fullUri": pytest.TEST_RESULT_LOAD_SOURCE,
                            "runNumber": 1,
                            "retryNumber": 0,
                            "status": "string",
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
                },
                kubernetes_name=pytest.TEST_KUBERNETES_NAME,
            )
        except Exception as e:
            print(e)


@pytest.fixture
def test_domain_job():
    with freeze_time(pytest.TEST_FROZE_DATE):
        yield Job(
            key=pytest.TEST_KEY,
            job_id=pytest.TEST_JOB_ID,
            job_configuration=RDFoxJobConfiguration(),
            neptune_load_id=pytest.TEST_NEPTUNE_LOAD_ID,
            job_created=datetime.now(),
            job_updated=datetime.now(),
            job_status=JobStatus.SCHEDULED,
            rdfox_statistics=InferenceStats(),
            rdfox_statistics_raw="""INFERENCETIME-13-Jul-2021 10:28:28|13-Jul-2021 10:28:40
    LOADTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:28
    TOTALTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:40""",
            neptune_statistics_raw={
                "status": "200 OK",
                "payload": {
                    "feedCount": [{"LOAD_FAILED": 0}],
                    "overallStatus": {
                        "fullUri": pytest.TEST_RESULT_LOAD_SOURCE,
                        "runNumber": 1,
                        "retryNumber": 0,
                        "status": "string",
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
            },
            kubernetes_name=pytest.TEST_KUBERNETES_NAME,
        )


@pytest.fixture
def repository_under_test():
    """
    Create database resource and mock table
    """
    with moto.mock_dynamodb2():
        job_repository_under_test = JobRepository()
        JobRepository().create_table_if_not_exists()
        yield job_repository_under_test
        JobRepository().delete_table()


@moto.mock_dynamodb2
@pytest.fixture
def create_test_job(repository, spec_override=None):
    key = ("2021-01-01",)
    spec = {"memory": 4096, "cores": 16, "key": key}
    if spec_override:
        spec = {**spec, **spec_override}
    job_id = repository.create_job(**spec)
    yield job_id
    repository.delete_job_by_id(job_id)


@moto.mock_dynamodb2
@pytest.fixture
def small_test_job(repository_under_test, create_test_job):
    """
    Create database resource and mock table
    """
    job_repository_under_test = repository_under_test
    job_id = create_test_job
    yield_val = job_id
    yield yield_val
    job_repository_under_test.delete_job_by_id(job_id)
