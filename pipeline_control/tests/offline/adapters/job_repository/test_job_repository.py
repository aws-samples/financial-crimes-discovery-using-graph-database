# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datetime

import moto
import pytest
from freezegun import freeze_time
from pyexpect import expect

from pipeline_control.adapters.job_repository.ddb_model import DDBJob
from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.domain.model import Job, JobStatus


@freeze_time(pytest.TEST_FROZE_DATE)
@moto.mock_dynamodb2
class TestRepository:
    def test_1_map_domain_model_to_ddb(self, repository_under_test, test_domain_job):
        ddb_model = repository_under_test.map_domain_model_to_ddb(test_domain_job)
        expect(type(ddb_model)).equals(DDBJob)

    def test_2_map_ddb_model_to_domain(
        self, repository_under_test, test_domain_job, test_ddb_job
    ):
        domain_model = repository_under_test.map_ddb_model_to_domain(test_ddb_job)
        expect(type(domain_model)).equals(Job)

    def test_3_create_job_success(self, repository_under_test):
        job_repository_under_test = repository_under_test
        job = Job(
            key=pytest.TEST_KEY,
        )

        with pytest.raises(Exception) as excinfo:
            job.job_id
        assert "Job id is available once Job is persisted" in str(excinfo.value)
        job_repository_under_test.save(job)
        queried_job = job_repository_under_test.get_job_by_id(
            f"{pytest.TEST_KEY}_{pytest.TEST_FROZE_DATE}_000"
        )
        expect(queried_job.job_id).to.equal(
            f"{pytest.TEST_KEY}_{pytest.TEST_FROZE_DATE}_000"
        )
        expect(type(queried_job.job_configuration)).to.equal(RDFoxJobConfiguration)
        expect(queried_job.job_status).to.be(JobStatus.CREATED)
        expect(queried_job.job_created).to.exist()
        expect(queried_job.job_updated).to.exist()
        expect(queried_job.neptune_writer_instance).to.equal("N/A")

    def test_4_update_job_if_job_exists(self, repository_under_test):
        job_repository_under_test = repository_under_test
        changed_kubernetes_name = "Schillok"
        updated_time_total_stat = 900
        tomorrow = datetime.datetime.now().date() + datetime.timedelta(days=1)

        job = Job(key=pytest.TEST_KEY)
        job_repository_under_test.save(job)

        job_queried = job_repository_under_test.get_job_by_id(
            f"{pytest.TEST_KEY}_{pytest.TEST_FROZE_DATE}_000"
        )
        job_queried.job_status = JobStatus.SCHEDULED
        job_queried.kubernetes_name = changed_kubernetes_name
        job_queried.rdfox_statistics.time_total = updated_time_total_stat

        expect(job_queried.is_dirty).to.equal(True)
        with freeze_time(tomorrow):
            job_repository_under_test.save(job_queried)
        expect(job_queried.is_dirty).to.equal(False)
        job_queried = job_repository_under_test.get_job_by_id(
            f"{pytest.TEST_KEY}_{pytest.TEST_FROZE_DATE}_000"
        )
        expect(job_queried.job_status).to.be(JobStatus.SCHEDULED)
        expect(job_queried.kubernetes_name).to.equal(changed_kubernetes_name)
        expect(job_queried.job_created.date()).to.equal(datetime.datetime.now().date())
        expect(job_queried.job_updated.date()).to.equal(tomorrow)
        expect(job_queried.rdfox_statistics.time_total).to.equal(
            updated_time_total_stat
        )
