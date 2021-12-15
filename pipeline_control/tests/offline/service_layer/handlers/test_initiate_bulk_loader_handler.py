# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pytest
from freezegun import freeze_time
from pyexpect import expect

from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStatProcessor,
    InferenceStats,
)
from pipeline_control.domain.model import Job, JobStatus


@freeze_time(pytest.TEST_FROZE_DATE)
class TestInitiateBulkloadHandler:
    def test_1_handle_upload_happy_pathend_to_end(
        self,
        g_post_inference_initiate_bulkload_handler_under_test,
        mocked_repository,
        g_post_inference_scheduled_test_job,
        g_inference_stats,
    ):
        g_post_inference_initiate_bulkload_handler_under_test.handle()
        queried_job: Job = mocked_repository.get_job_by_id(
            g_post_inference_scheduled_test_job.job_id
        )
        expect(queried_job.job_status).to.equal(JobStatus.NEPTUNE_LOAD_IN_PROGRESS)
        expect(queried_job.neptune_load_id).to.equal(pytest.TEST_NEPTUNE_LOAD_ID)
        expect(queried_job.job_configuration.neptune_configuration.source).to.equal(
            g_post_inference_initiate_bulkload_handler_under_test.source
        )
        expect(queried_job.neptune_writer_instance).to.equal(
            pytest.TEST_NEPTUNE_WRITER_INSTANCE
        )
