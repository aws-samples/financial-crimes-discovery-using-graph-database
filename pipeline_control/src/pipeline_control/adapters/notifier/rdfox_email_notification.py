# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass
from typing import List, Optional

from pipeline_control.adapters.notifier.email_notification import EmailNotification

SECONDS_PER_HOUR = 60 * 60

SUBJECT_TEMPLATE = """
Inference Result Notification for {job_id} - {job_status}
"""

EMAIL_TEMPLATE = """
The job {job_id} completed at {job_updated} with status {job_status}

# Overview #
Data set: {data_set}
Full chains: {full_chains_amount}
Partial chains: {partial_chains_amount}
Error count: {error_count}
Time to analyse: {time_to_process} hours
Time to load into Neptune: {time_to_load} hours

If the Job was configured to remain active you can connect to the RDFox endpoint using its well known endpoint
"""


@dataclass
class RDFoxEmailNotification(EmailNotification):
    job_id: str
    job_status: str
    data_set: str
    job_updated: str
    full_chains_amount: str
    partial_chains_amount: str
    neptune_load_id: str
    load_errors: Optional[List]
    time_to_process: int
    time_to_load: int
    rdfox_endpoint: Optional[str]

    @property
    def subject(self):
        return f"Inference Result Notification for {self.job_id} - {self.job_status}"

    @property
    def message(self):
        email_message = EMAIL_TEMPLATE.format(
            job_id=self.job_id,
            job_updated=self.job_updated,
            job_status=self.job_status,
            data_set=self.data_set,
            partial_chains_amount=self.partial_chains_amount,
            full_chains_amount=self.full_chains_amount,
            error_count=len(self.load_errors),
            time_to_process=self.time_to_process / SECONDS_PER_HOUR,
            time_to_load=self.time_to_load / SECONDS_PER_HOUR,
            # rdfox_endpoint=self.rdfox_endpoint,
        )
        return email_message
