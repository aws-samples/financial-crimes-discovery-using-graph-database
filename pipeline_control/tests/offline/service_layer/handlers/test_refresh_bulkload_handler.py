# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from pyexpect import expect

from pipeline_control.domain.model import JobStatus


class TestRefreshBulkLoad:
    def test_1_update_status_loading(
        self,
        mocked_repository,
        bulkloading_job,
        refresh_bulkload_handler,
        g_neptune_load_in_progress,
        g_post_inference_fake_neptune_loader_factory,
    ):
        g_post_inference_fake_neptune_loader_factory.set_loading()
        refresh_bulkload_handler.handle()
        retrieved_job = mocked_repository.get_job_by_id(bulkloading_job.job_id)
        expect(retrieved_job.neptune_statistics_raw).equals(g_neptune_load_in_progress)
        g_post_inference_fake_neptune_loader_factory.set_complete()
        refresh_bulkload_handler.handle()
        retrieved_job = mocked_repository.get_job_by_id(bulkloading_job.job_id)

        expect(retrieved_job.job_status).equals(JobStatus.NEPTUNE_LOAD_COMPLETED)
        expect(retrieved_job.neptune_statistics.records_total).equals(41220091)
