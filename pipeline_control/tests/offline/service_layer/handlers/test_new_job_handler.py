# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import pytest
from freezegun import freeze_time
from pyexpect import expect

from pipeline_control.domain.model import JobStatus

logger = logging.getLogger("test_scheduler")
logger.setLevel(logging.WARN)


@freeze_time(pytest.TEST_FROZE_DATE)
class TestNewJobHandler:
    @pytest.mark.usefixtures(
        "seeded_source_bucket_for_test",
        "fake_eks_cluster",
        "test_job_spec_json",
        "mocked_hikaru_create",
    )
    def test_1_handle_job_creation(
        self,
        new_job_handler_under_test,
        mocked_repository,
        mocked_hikaru_read,
        mocked_pod_read,
    ):
        new_job_handler_under_test.handle()
        queried_job = mocked_repository.get_job_by_id(pytest.DERIVED_JOB_ID)
        expect(queried_job).to.exist()
        expect(queried_job.job_status).to.equal(JobStatus.SCHEDULED)
        expect(type(queried_job.kubernetes_name)).to.exist()
        expect(queried_job.kubernetes_worker_type).to.contain(
            pytest.TEST_WORKER_NODE_TYPE
        )
