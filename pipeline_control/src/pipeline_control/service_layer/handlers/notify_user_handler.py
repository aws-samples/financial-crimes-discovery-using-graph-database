# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from pipeline_control.adapters.notifier.rdfox_email_notification import (
    RDFoxEmailNotification,
)
from pipeline_control.domain import commands
from pipeline_control.domain.model import Job, JobStatus

from .handler import Handler

logger = logging.getLogger(__name__)


class NotifyUserHandler(Handler):
    def __init__(self, cmd: commands.NotifyUser):
        self.job_repository = cmd.job_repository
        self.notifier = cmd.notifier

    def handle(self):
        all_complete_jobs = self.job_repository.get_all_by_status(
            JobStatus.NEPTUNE_LOAD_COMPLETED
        )

        all_notifiable_jobs = [
            [job, JobStatus.SUCCESS_NOTIFICATION_SENT] for job in all_complete_jobs
        ]
        all_failed_jobs = self.job_repository.get_all_by_status(
            JobStatus.NEPTUNE_LOAD_FAILED
        )
        all_notifiable_jobs = all_notifiable_jobs + [
            [job, JobStatus.ERROR_NOTIFICATION_SENT] for job in all_failed_jobs
        ]

        logger.info(f"Found {len(all_notifiable_jobs)} jobs in appropriate status")
        for job_entry in all_notifiable_jobs:

            job, status = job_entry
            self.handle_job(job, status)

    def handle_job(self, job: Job, desired_status):
        job = self.job_repository.get_job_by_id(job.job_id)
        notification = self.make_notification(job)
        self.notifier.send_message(notification)
        job.job_status = desired_status
        logger.info(
            f"Notification sent - Updating status of {job.job_id} to {desired_status}"
        )
        self.job_repository.save(job)

    def make_notification(self, job):
        notification = RDFoxEmailNotification(
            job_id=job.job_id,
            job_status=str(job.job_status),
            data_set=job.key,
            job_updated=job.job_updated,
            full_chains_amount=job.rdfox_statistics.full_chains_amount,
            partial_chains_amount=job.rdfox_statistics.partial_chains_amount,
            neptune_load_id=job.neptune_load_id,
            load_errors=[],
            time_to_process=job.rdfox_statistics.time_total,
            time_to_load=job.neptune_statistics.time_total,
            rdfox_endpoint="TBC",
        )
        return notification
