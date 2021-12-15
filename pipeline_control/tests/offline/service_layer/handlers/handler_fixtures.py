# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import tempfile
from unittest import mock

import boto3
import moto
import pytest
from freezegun.api import freeze_time
from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

from pipeline_control.adapters.job_repository.job_repository import Job
from pipeline_control.adapters.neptune_loader.neptune_loader_factory import (
    NeptuneLoaderFactory,
)
from pipeline_control.adapters.notifier.sns_notifier import SNSNotifier
from pipeline_control.domain.commands import CreateNewJob, NotifyUser, RefreshBulkload
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStatProcessor,
)
from pipeline_control.domain.model import JobStatus
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStatProcessor,
    NeptuneStats,
)
from pipeline_control.service_layer.handlers.new_job_handler import NewJobHandler
from pipeline_control.service_layer.handlers.notify_user_handler import (
    NotifyUserHandler,
)
from pipeline_control.service_layer.handlers.refresh_bulkload_handler import (
    RefreshBulkloadHandler,
)


@pytest.fixture
def test_job_spec_json():
    return {
        "requested_cores": 4,
        "requested_memory": 2048,
        "init_container_image": "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/pre-rdfox:latest",
        "publisher_container_image": "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/post-rdfox:latest",
        "rdfox_container_image": "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/custom-rdfox:latest",
        "rdfox_init_container_image": "oxfordsemantic/rdfox-init",
        "auto_shutdown": False,
        "job_bucket": pytest.TEST_BUCKET_NAME,
        "job_key": pytest.TEST_KEY,
    }


@pytest.fixture
def seeded_source_bucket_for_test(test_job_spec_json):
    _, path = tempfile.mkstemp()
    with open(path, "wb") as data:
        data.write(bytes(json.dumps(test_job_spec_json), "utf-8"))

    with moto.mock_s3():
        s3 = boto3.resource("s3")
        bucket = s3.create_bucket(
            Bucket=pytest.TEST_BUCKET_NAME,
            CreateBucketConfiguration={
                "LocationConstraint": "ap-southeast-1",
            },
        )
        with open(path, "rb") as data:
            bucket.upload_fileobj(data, pytest.TEST_JOBSPEC_KEY)
        yield bucket

        bucket.delete_objects(
            Delete={
                "Objects": [
                    {
                        "Key": pytest.TEST_JOBSPEC_KEY,
                    }
                ]
            }
        )
        bucket.delete()


@pytest.fixture
def new_job_handler_under_test(new_job_command):
    handler = NewJobHandler(cmd=new_job_command)
    return handler


@pytest.fixture
def new_job_command(
    mocked_repository,
    g_infrastructure_fake_kubernetes_client_factory,
    seeded_source_bucket_for_test,
):
    return CreateNewJob(
        job_repository=mocked_repository,
        s3_bucket_name=seeded_source_bucket_for_test.name,
        api_client_factory=g_infrastructure_fake_kubernetes_client_factory,
        key=pytest.TEST_JOBSPEC_KEY,
        job_configuration_name=pytest.JOBSPEC_NAME,
    )


@pytest.fixture
def bulkloading_job(mocked_repository):
    with freeze_time(pytest.TEST_FROZE_DATE):
        loading_job = Job(key=pytest.TEST_KEY)
        mocked_repository.save(loading_job)
        loading_job.job_status = JobStatus.NEPTUNE_LOAD_IN_PROGRESS
        loading_job.neptune_load_id = pytest.TEST_NEPTUNE_LOAD_ID
        mocked_repository.save(loading_job)
        yield loading_job


@pytest.fixture
def refresh_bulkload_command(
    bulkloading_job,
    mocked_repository,
    entrypoint_fake_neptune_loader_complete_after_10,
    g_post_inference_fake_neptune_loader_factory,
):
    entrypoint_fake_neptune_loader_complete_after_10.initiate_bulk_load()
    yield RefreshBulkload(
        job_repository=mocked_repository,
        neptune_stat_processor=NeptuneStatProcessor(),
        neptune_loader_factory=g_post_inference_fake_neptune_loader_factory,
    )


@pytest.fixture
def refresh_bulkload_handler(refresh_bulkload_command):
    yield RefreshBulkloadHandler(cmd=refresh_bulkload_command)


@pytest.fixture
def mocked_sns_topic():
    with moto.mock_sns() as mocked_sns:
        sns_client = boto3.client("sns")
        notification_response = sns_client.create_topic(
            Name=pytest.TEST_NOTIFICATION_TOPIC
        )
        notification_arn = notification_response["TopicArn"]
        yield notification_arn
        sns_client.delete_topic(TopicArn=notification_arn)


@pytest.fixture
def mocked_sns_notifier(mocked_sns_topic):
    sns_notifier = SNSNotifier(topic_arn=mocked_sns_topic)
    wrapped_sns_notifier = mock.Mock(wraps=sns_notifier)
    yield wrapped_sns_notifier


@pytest.fixture
def notify_user_command(mocked_repository, mocked_sns_notifier):
    yield NotifyUser(job_repository=mocked_repository, notifier=mocked_sns_notifier)


@pytest.fixture
def completed_job(
    mocked_repository,
    g_neptune_load_complete_adjusted,
    g_inference_stats,
):
    inference_stats_string = g_inference_stats.decode("utf-8")
    rdfox_statistics = InferenceStatProcessor(
        inference_stats=inference_stats_string,
    ).process_inference()
    neptune_statistics = NeptuneStatProcessor().process(
        stat_dict=g_neptune_load_complete_adjusted
    )
    with freeze_time(pytest.TEST_FROZE_DATE):
        complete_job = Job(key=pytest.TEST_KEY)
        mocked_repository.save(complete_job)
        complete_job.job_status = JobStatus.NEPTUNE_LOAD_COMPLETED
        complete_job.neptune_statistics = neptune_statistics
        complete_job.rdfox_statistics = rdfox_statistics
        mocked_repository.save(complete_job)
        yield complete_job


@pytest.fixture
def notify_user_handler_under_test(notify_user_command):
    yield NotifyUserHandler(cmd=notify_user_command)
