# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import tempfile
import unittest

import boto3
import moto
import pytest
from freezegun.api import freeze_time
from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

from pipeline_control.adapters.neptune_loader.fake_neptune_loader import (
    FakeNeptuneLoader,
)
from pipeline_control.adapters.neptune_loader.fake_neptune_loader_factory import (
    FakeNeptuneLoaderFactory,
)
from pipeline_control.domain.commands import InitiateBulkload, ProcessInference
from pipeline_control.domain.inference_stat_processor.fake_inference_stat_processor import (
    FakeInferenceStatProcessor,
)
from pipeline_control.domain.model import Job, JobStatus
from pipeline_control.service_layer.handlers.initiate_bulk_load_handler import (
    InitiateBulkloadHandler,
)
from pipeline_control.service_layer.handlers.process_inference_handler import (
    ProcessInferenceHandler,
)


@pytest.fixture
def entrypoint_s3_event_rdfoxlog_upload(s3_event_jobspec_upload):
    rdfoxlog_upload = s3_event_jobspec_upload.copy()
    rdfoxlog_upload["Records"][0]["s3"]["object"]["key"] = pytest.TEST_RESULT_KEY
    rdfoxlog_upload["Records"][0]["s3"]["bucket"]["name"] = pytest.TEST_RESULT_BUCKET
    return rdfoxlog_upload


@pytest.fixture
def s3_event_jobspec_upload():
    return {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "ap-southeast-1",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {"principalId": "EXAMPLE"},
                "requestParameters": {"sourceIPAddress": "127.0.0.1"},
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": f"{pytest.TEST_BUCKET_NAME}",
                        "ownerIdentity": {"principalId": "EXAMPLE"},
                        "arn": "arn:aws:s3:::example-bucket",
                    },
                    "object": {
                        "key": f"{pytest.TEST_JOBSPEC_KEY}",
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901",
                    },
                },
            }
        ]
    }


@pytest.fixture()
def g_post_inference_scheduled_test_job(
    mocked_repository, g_job_configurations_small_rdfox_job_configuration
):
    with freeze_time(pytest.TEST_FROZE_DATE):
        the_g_post_inference_scheduled_test_job = Job(key=pytest.TEST_KEY)
        the_g_post_inference_scheduled_test_job.job_configuration = (
            g_job_configurations_small_rdfox_job_configuration
        )
        mocked_repository.save(the_g_post_inference_scheduled_test_job)
        the_g_post_inference_scheduled_test_job.job_status = JobStatus.SCHEDULED
        mocked_repository.save(the_g_post_inference_scheduled_test_job)
        yield the_g_post_inference_scheduled_test_job


@pytest.fixture
def g_neptune_load_in_progress(neptune_load_template):
    as_dict = json.loads(neptune_load_template)
    as_dict["payload"]["overallStatus"]["status"] = "LOAD_IN_PROGRESS"
    yield as_dict


@pytest.fixture
def g_neptune_load_complete(neptune_load_template):
    as_dict = json.loads(neptune_load_template)
    yield as_dict


@pytest.fixture
def g_neptune_load_complete_adjusted(neptune_load_template):
    as_dict = json.loads(neptune_load_template)
    as_dict["payload"]["overallStatus"]["status"] = "LOAD_COMPLETE"
    yield as_dict


@pytest.fixture
def neptune_load_template():
    with open("tests/data/neptune_load_template.json", "rb") as data:
        yield data.read()


@pytest.fixture
def neptune_instance_response_template():
    with open("tests/data/neptune_instance_response.json", "rb") as data:
        yield data.read()


@pytest.fixture
def neptune_cluster_response_template():
    with open("tests/data/neptune_cluster_response.json", "rb") as data:
        yield data.read()


@pytest.fixture
def small_test_triples():
    with open("tests/data/small_triples.nt", "rb") as data:
        yield data.read()


@pytest.fixture
def g_inference_stats():
    with open("tests/data/inference_stats.log", "rb") as data:
        yield data.read()


@moto.mock_sts
@pytest.fixture
def entrypoint_fake_neptune_loader_complete_after_10(
    g_job_configurations_neptune_configuration,
    g_neptune_load_in_progress,
    g_neptune_load_complete,
):
    return FakeNeptuneLoader(
        fake_load_id=pytest.TEST_NEPTUNE_LOAD_ID,
        complete_after_iterations=10,
        load_stats=g_neptune_load_in_progress,
        success_stats=g_neptune_load_complete,
        neptune_load_configuration=g_job_configurations_neptune_configuration,
    )


@pytest.fixture
def g_post_inference_fake_neptune_loader_factory(
    g_neptune_load_in_progress,
    g_neptune_load_complete,
    g_job_configurations_neptune_configuration,
):
    yield FakeNeptuneLoaderFactory(
        fake_load_id=pytest.TEST_NEPTUNE_LOAD_ID,
        complete_after_iterations=10,
        load_stats=g_neptune_load_in_progress,
        success_stats=g_neptune_load_complete,
        neptune_load_configuration=g_job_configurations_neptune_configuration,
    )


@pytest.fixture
def s3_result_bucket():
    with moto.mock_s3():
        s3 = boto3.resource("s3")
        bucket = s3.create_bucket(
            Bucket=pytest.TEST_RESULT_BUCKET,
            CreateBucketConfiguration={
                "LocationConstraint": "ap-southeast-1",
            },
        )
        _, path = tempfile.mkstemp()
        with open(path, "rb") as data:
            bucket.upload_fileobj(data, pytest.TEST_RESULT_KEY)
        yield bucket

        # bucket.delete()


@pytest.fixture
def upload_rdfoxlog_to_s3(s3_result_bucket, entrypoint_s3_event_rdfoxlog_upload):
    _, path = tempfile.mkstemp()
    with open(path, "wb") as data:
        data.write(bytes(json.dumps(entrypoint_s3_event_rdfoxlog_upload), "utf-8"))

    with open(path, "rb") as data:
        s3_result_bucket.upload_fileobj(data, pytest.TEST_RESULT_KEY)

        yield data

    s3_result_bucket.delete_objects(
        Delete={
            "Objects": [
                {
                    "Key": pytest.TEST_RESULT_KEY,
                }
            ]
        }
    )


@pytest.fixture
def upload_triples_to_s3(
    s3_result_bucket, g_post_inference_scheduled_test_job, small_test_triples
):

    _, triples_file = tempfile.mkstemp()
    job_id = g_post_inference_scheduled_test_job.job_id
    triples_object_key = f"{job_id}/sometriple.nt"

    with open(triples_file, "wb") as data:
        data.write(small_test_triples)

    with open(triples_file, "rb") as data:
        s3_result_bucket.upload_fileobj(data, triples_object_key)
        yield s3_result_bucket

    s3_result_bucket.delete_objects(
        Delete={
            "Objects": [
                {
                    "Key": triples_object_key,
                }
            ]
        }
    )


@pytest.fixture
def seeded_s3_result_bucket(upload_rdfoxlog_to_s3, upload_triples_to_s3):
    yield (upload_triples_to_s3, upload_rdfoxlog_to_s3)[0]


@pytest.fixture
def post_inference_handler_under_test(
    process_inference_command, g_post_inference_scheduled_test_job
):
    handler = ProcessInferenceHandler(cmd=process_inference_command)
    return handler


@pytest.fixture
def g_post_inference_initiate_bulkload_handler_under_test(
    process_inference_bulkload_command,
    g_post_inference_fake_neptune_cluster_response,
):
    handler = InitiateBulkloadHandler(cmd=process_inference_bulkload_command)
    return handler


@pytest.fixture
def g_post_inference_fake_neptune_cluster_response(
    neptune_instance_response_template, neptune_cluster_response_template
):
    describe_instance_response = json.loads(neptune_instance_response_template)
    describe_instance_response["DBInstances"][0][
        "DBInstanceClass"
    ] = pytest.TEST_NEPTUNE_WRITER_INSTANCE

    describe_cluster_response = json.loads(neptune_cluster_response_template)
    describe_cluster_response["DBClusters"][0]["DBClusterMembers"][0][
        "DBInstanceIdentifier"
    ] = "somethingortheother"

    def neptune_make_api_call(*args, **kwargs):
        obj, operation, kwargs = args
        ret = None
        if operation == "DescribeDBClusters":
            ret = describe_cluster_response
        elif operation == "DescribeDBInstances":
            ret = describe_instance_response
        return ret

    with unittest.mock.patch(
        "botocore.client.BaseClient._make_api_call", new=neptune_make_api_call
    ) as mocked_neptune:
        yield mocked_neptune


@pytest.fixture
def process_inference_command(
    mocked_repository,
    s3_result_bucket,
    g_inference_stats,
):
    inference_stats_string = g_inference_stats.decode("utf-8")
    return ProcessInference(
        job_id=pytest.TEST_JOB_ID,
        job_repository=mocked_repository,
        s3_bucket_name=s3_result_bucket.name,
        key=pytest.TEST_RESULT_KEY,
        inference_stat_processor=FakeInferenceStatProcessor(
            inference_stats=inference_stats_string,
        ),
    )


@pytest.fixture
def process_inference_bulkload_command(
    mocked_repository,
    g_post_inference_fake_neptune_loader_factory,
    s3_result_bucket,
    g_inference_stats,
    seeded_s3_result_bucket,
):
    yield InitiateBulkload(
        job_id=pytest.TEST_JOB_ID,
        job_repository=mocked_repository,
        neptune_loader_factory=g_post_inference_fake_neptune_loader_factory,
        source=pytest.TEST_RESULT_LOAD_SOURCE.split("/")[:-1],
    )


@pytest.fixture
def g_post_inference_mock_sigv4_signer():
    with moto.mock_sts():
        yield SigV4Signer()
