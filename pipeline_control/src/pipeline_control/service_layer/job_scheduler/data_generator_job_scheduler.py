# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from pipeline_control.adapters.kubernetes_objects.data_generator_job import (
    DataGeneratorJob,
)
from pipeline_control.domain.model import Job
from pipeline_control.service_layer.job_scheduler.job_scheduler import JobScheduler


class DataGeneratorJobScheduler(JobScheduler):
    def create_kubernetes_job(self) -> Job:
        job = DataGeneratorJob(
            job_configuration=self.job_configuration,
            client=self.api_client,
        )
        return job
