# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest

import pytest

from pipeline_control.adapters.job_repository.fake_job_repository import (
    FakeJobRepository,
)
from pipeline_control.adapters.neptune_loader.fake_neptune_loader import (
    FakeNeptuneLoader,
)
from pipeline_control.domain.commands import CreateNewJob, RefreshBulkload
from pipeline_control.domain.inference_stat_processor.fake_inference_stat_processor import (
    FakeInferenceStatProcessor,
)
from pipeline_control.domain.model import Job
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStatProcessor,
)
from pipeline_control.service_layer.eks_control.util.fake_eks_client_factory import (
    FakeKubernetesClientFactory,
)


@pytest.fixture
def entrypoint_created_job():
    return Job(
        key=pytest.TEST_KEY,
        job_id=pytest.TEST_JOB_ID,
    )


@pytest.fixture
def entrypoint_fake_neptune_loader(g_job_configurations_neptune_configuration):
    fake_neptune_loader = FakeNeptuneLoader()
    fake_neptune_loader.neptune_configuration = (
        g_job_configurations_neptune_configuration
    )
    return fake_neptune_loader


@pytest.fixture
def entrypoint_fake_new_job_command(entrypoint_fake_neptune_loader):
    return CreateNewJob(
        s3_bucket_name=pytest.TEST_BUCKET_NAME,
        key=pytest.TEST_KEY,
        job_repository=FakeJobRepository(),
        job_id=pytest.TEST_JOB_ID,
        neptune_loader=entrypoint_fake_neptune_loader,
        inference_file_name="rdfox.log",
        api_client_factory=FakeKubernetesClientFactory(pytest.TEST_CLUSTER_NAME),
        inference_stat_processor=FakeInferenceStatProcessor(),
    )


@pytest.fixture
def entrypoint_fake_process_inference_command():
    return CreateNewJob(
        s3_bucket_name=pytest.TEST_BUCKET_NAME,
        key=pytest.TEST_KEY,
        job_repository=FakeJobRepository(),
        job_configuration_name=".jobspec.json",
        api_client_factory=FakeKubernetesClientFactory(pytest.TEST_CLUSTER_NAME),
    )


@pytest.fixture
def entrypoint_fake_refresh_bulkload_command():
    with unittest.mock.patch(
        "pipeline_control.domain.commands.RefreshBulkload", autospec=True
    ) as entrypoint_ake_refresh_bulkload_command:
        entrypoint_ake_refresh_bulkload_command.return_value = unittest.mock.MagicMock()
        yield entrypoint_ake_refresh_bulkload_command


@pytest.fixture
def entrypoint_fake_new_job_handler():
    with unittest.mock.patch(
        "pipeline_control.service_layer.handlers.new_job_handler.NewJobHandler",
        autospec=True,
    ) as mock_new_job_handler:
        handle = unittest.mock.MagicMock(return_value="")
        mock_new_job_handler.handle = handle
        yield mock_new_job_handler


@pytest.fixture
def entrypoint_fake_initiate_bulk_load_handler():
    with unittest.mock.patch(
        "pipeline_control.service_layer.handlers.initiate_bulk_load_handler.InitiateBulkloadHandler",
        autospec=True,
    ) as mock_initiate_bulk_load_handler:
        handle = unittest.mock.MagicMock(return_value="")
        mock_initiate_bulk_load_handler.handle = handle
        yield mock_initiate_bulk_load_handler


@pytest.fixture
def entrypoint_fake_refresh_bulkload_handler():
    with unittest.mock.patch(
        "pipeline_control.service_layer.handlers.refresh_bulkload_handler.RefreshBulkloadHandler",
        autospec=True,
    ) as mock_refresh_bulkload_handler:
        handle = unittest.mock.MagicMock(return_value="")
        mock_refresh_bulkload_handler.handle = handle
        yield mock_refresh_bulkload_handler


@pytest.fixture
def entrypoint_fake_process_inference_handler():
    with unittest.mock.patch(
        "pipeline_control.service_layer.handlers.process_inference_handler.ProcessInferenceHandler",
        autospec=True,
    ) as mock_process_inference_handler:
        handle = unittest.mock.MagicMock(return_value="lah")
        mock_process_inference_handler.handle = handle
        yield mock_process_inference_handler


@pytest.fixture
def entrypoint_fake_notify_user_handler():
    with unittest.mock.patch(
        "pipeline_control.service_layer.handlers.notify_user_handler.NotifyUserHandler",
        autospec=True,
    ) as mock_notify_user_handler:
        handle = unittest.mock.MagicMock(return_value="")
        mock_notify_user_handler.handle = handle
        yield mock_notify_user_handler


@pytest.fixture
def entrypoint_s3_event_rdfoxlog_upload(s3_event_jobspec_upload):
    rdfoxlog_upload = s3_event_jobspec_upload.copy()
    rdfoxlog_upload["Records"][0]["s3"]["object"]["key"] = pytest.TEST_RESULT_KEY
    rdfoxlog_upload["Records"][0]["s3"]["bucket"]["name"] = pytest.TEST_RESULT_BUCKET
    return rdfoxlog_upload


@pytest.fixture
def entrypoint_s3_event_not_jobspec_upload(s3_event_jobspec_upload):
    other_key_upload = s3_event_jobspec_upload.copy()
    other_key_upload["Records"][0]["s3"]["object"]["key"] = "somethingelse"
    return other_key_upload


@pytest.fixture
def entrypoint_s3_event_not_rdfoxlog_upload(entrypoint_s3_event_not_jobspec_upload):
    return entrypoint_s3_event_not_jobspec_upload


@pytest.fixture
def entrypoint_time_based_event():
    yield {
        "version": "0",
        "id": "53dc4d37-cffa-4f76-80c9-8b7d4a4d2eaa",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2015-10-08T16:53:06Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/my-scheduled-rule"],
        "detail": {},
    }


@pytest.fixture
def entrypoint_not_time_based_event(entrypoint_time_based_event):
    not_time = entrypoint_time_based_event.copy()
    not_time["detail-type"] = "Glumanda Event"
    yield not_time
