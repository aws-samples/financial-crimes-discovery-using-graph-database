# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest

import pytest

from pipeline_control.entrypoints import lambda_entry_points


@pytest.fixture
def entrypoint_fake_process_inference_command():
    with unittest.mock.patch(
        "pipeline_control.domain.commands.ProcessInference", autospec=True
    ) as entrypoint_fake_process_inference_command:
        entrypoint_fake_process_inference_command.return_value = (
            unittest.mock.MagicMock()
        )
        yield entrypoint_fake_process_inference_command


class TestProcessInferenceLambdaHandler:
    # TODO: This should fail if we download the wrong file format
    @pytest.mark.usefixtures("upload_rdfoxlog_to_s3")
    def test_1_perform_post_inference_if_rdfoxlog_uploaded(
        self,
        entrypoint_s3_event_rdfoxlog_upload,
        entrypoint_fake_process_inference_handler,
        entrypoint_fake_process_inference_command,
        entrypoint_fake_initiate_bulk_load_handler,
        g_post_inference_scheduled_test_job,
    ):
        lambda_entry_points.handle_process_inference(
            entrypoint_s3_event_rdfoxlog_upload, {}
        )

        entrypoint_fake_process_inference_command.assert_called_with(
            s3_bucket_name=pytest.TEST_RESULT_BUCKET,
            key=pytest.TEST_RESULT_DATA_KEY,
            job_repository=unittest.mock.ANY,
            job_id=pytest.TEST_JOB_ID,
            inference_stat_processor=unittest.mock.ANY,
        )
        entrypoint_fake_process_inference_handler.assert_called_once()
        entrypoint_fake_initiate_bulk_load_handler.assert_called_once()

    def test_2_dontprocess_if_other_uploaded(
        self,
        entrypoint_s3_event_not_rdfoxlog_upload,
        entrypoint_fake_process_inference_handler,
    ):
        lambda_entry_points.handle_input_upload(
            entrypoint_s3_event_not_rdfoxlog_upload, {}
        )
        entrypoint_fake_process_inference_handler.assert_not_called()
