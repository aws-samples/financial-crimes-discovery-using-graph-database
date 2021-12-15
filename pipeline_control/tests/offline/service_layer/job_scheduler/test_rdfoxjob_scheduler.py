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
class TestRDFoxJobScheduler:
    def test_1_create_new_job(self, a_rdfox_job, mocked_repository):
        queried = mocked_repository.get_job_by_id(a_rdfox_job.job_id)
        expect(queried).to.exist()
        expect(queried.job_status).to.equal(JobStatus.CREATED)

    def test_2_schedule_kubernetes_job(
        self,
        mocked_hikaru_create,
        mocked_hikaru_read,
        mocked_repository,
        mocked_pod_read,
        job_scheduler_under_test,
        a_rdfox_job,
    ):
        rdfox_job = job_scheduler_under_test.create_kubernetes_job()
        job_scheduler_under_test.schedule_kubernetes_job(
            job=a_rdfox_job, kubernetes_job=rdfox_job
        )
        queried_job = mocked_repository.get_job_by_id(a_rdfox_job.job_id)
        expect(queried_job).to.exist()
        expect(queried_job.kubernetes_name).to.equal(mocked_hikaru_create)
        expect(queried_job.job_status).to.equal(JobStatus.SCHEDULED)
