# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import annotations

from typing import Optional

from kubernetes.client.api_client import ApiClient

from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.domain.commands import Command
from pipeline_control.service_layer.handlers.handler import Handler
from pipeline_control.service_layer.job_scheduler.rdfoxjob_scheduler import (
    RDFoxJobScheduler,
)
from pipeline_control.service_layer.s3_json_loader import S3JsonLoader


class NewJobHandler(Handler):
    def __init__(self, cmd: Command.CreateNewJob):
        self.s3_bucket_name = cmd.s3_bucket_name
        self.key = cmd.key
        self.job_repository = cmd.job_repository
        self.api_client_factory = cmd.api_client_factory

    def handle(
        self,
    ):
        scheduler = self._make_scheduler(job_configuration=self.get_job_configuration())
        return scheduler.create_and_schedule_new_job()

    @property
    def api_client(self):
        return self.api_client_factory.get_client()

    def get_job_configuration(self) -> RDFoxJobConfiguration:
        jobconfiguration_dict = self._try_to_download_job_configuration_from_s3()
        job_spec = RDFoxJobConfiguration.from_dict(jobconfiguration_dict)
        return job_spec

    def _make_scheduler(
        self,
        job_configuration: RDFoxJobConfiguration,
        api_client: Optional[ApiClient] = None,
        job_repository: Optional[JobRepository] = None,
    ):
        if not api_client:
            api_client = self.api_client
        if not job_repository:
            job_repository = self.job_repository

        return RDFoxJobScheduler(
            job_repository=job_repository,
            api_client=api_client,
            job_configuration=job_configuration,
        )

    def _try_to_download_job_configuration_from_s3(self):
        return S3JsonLoader.download_and_load_json_from_s3(
            bucket_name=self.s3_bucket_name,
            key=f"{self.key}",
        )
