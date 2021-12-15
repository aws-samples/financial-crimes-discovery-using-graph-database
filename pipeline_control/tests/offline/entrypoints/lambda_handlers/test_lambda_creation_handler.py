# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest

import pytest

from pipeline_control.domain.model import Job
from pipeline_control.entrypoints import lambda_entry_points


@pytest.fixture
def entrypoint_fake_new_job_handler(entrypoint_created_job):
    with unittest.mock.patch(
        "pipeline_control.service_layer.handlers.new_job_handler.NewJobHandler.handle",
        autospec=True,
    ) as fake_job_handler:
        fake_job_handler.return_value = entrypoint_created_job
        yield fake_job_handler


@pytest.fixture
def fake_create_new_job_command():
    with unittest.mock.patch(
        "pipeline_control.domain.commands.CreateNewJob", autospec=True
    ) as fake_create_new_job_command:
        fake_create_new_job_command.return_value = unittest.mock.MagicMock()
        yield fake_create_new_job_command


class TestNewJobLambdaHandler:
    def test_1_create_job_if_appspec_uploaded(
        self,
        s3_event_jobspec_upload,
        entrypoint_fake_new_job_handler,
        fake_create_new_job_command,
    ):
        lambda_entry_points.handle_input_upload(s3_event_jobspec_upload, {})

        fake_create_new_job_command.assert_called_with(
            s3_bucket_name=pytest.TEST_BUCKET_NAME,
            key=pytest.TEST_JOBSPEC_KEY,
            job_repository=unittest.mock.ANY,
            job_configuration_name=unittest.mock.ANY,
            api_client_factory=unittest.mock.ANY,
        )
        entrypoint_fake_new_job_handler.assert_called_once()

    def test_2_dontcreate_job_if_other_uploaded(
        self, entrypoint_s3_event_not_jobspec_upload, entrypoint_fake_new_job_handler
    ):
        lambda_entry_points.handle_input_upload(
            entrypoint_s3_event_not_jobspec_upload, {}
        )
        entrypoint_fake_new_job_handler.assert_not_called()
