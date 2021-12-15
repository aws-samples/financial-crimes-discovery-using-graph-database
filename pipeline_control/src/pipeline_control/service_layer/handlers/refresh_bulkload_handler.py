# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from pipeline_control.domain import commands
from pipeline_control.domain.model import Job, JobStatus

from .handler import Handler

logger = logging.getLogger(__name__)


class RefreshBulkloadHandler(Handler):
    def __init__(self, cmd: commands.RefreshBulkload):
        self.job_repository = cmd.job_repository
        self.neptune_loader_factory = cmd.neptune_loader_factory
        self.neptune_stat_processor = cmd.neptune_stat_processor

    def handle(self):
        all_loading_jobs = self.job_repository.get_all_by_status(
            JobStatus.NEPTUNE_LOAD_IN_PROGRESS
        )
        all_loading_jobs = all_loading_jobs + self.job_repository.get_all_by_status(
            JobStatus.NEPTUNE_LOAD_IN_QUEUE
        )
        all_loading_jobs = all_loading_jobs + self.job_repository.get_all_by_status(
            JobStatus.NEPTUNE_LOAD_NOT_STARTED
        )
        logger.info(f"Found {len(all_loading_jobs)} jobs in appropriate status")
        for job in all_loading_jobs:
            self.handle_job(job)

    def handle_job(self, job: Job):
        logger.info(f"Updating load status of {job.job_id} {job.neptune_load_id}")
        job = self.job_repository.get_job_by_id(job.job_id)
        neptune_configuration = job.job_configuration.neptune_configuration
        neptune_loader = self.neptune_loader_factory.make_read_only_loader(
            neptune_load_id=job.neptune_load_id,
            override_neptune_load_configuration=neptune_configuration,
        )
        status = neptune_loader.get_status()
        status_raw = status.raw
        job.neptune_statistics_raw = status_raw
        job.neptune_statistics = self.neptune_stat_processor.process(status_raw)
        job.job_status = JobStatus(f"NEPTUNE_{job.neptune_statistics.status}")
        self.job_repository.save(job)
