# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from pipeline_control.domain import commands
from pipeline_control.domain.model import JobStatus
from pipeline_control.service_layer.handlers.handler import Handler

logger = logging.getLogger(__name__)


class ProcessInferenceHandler(Handler):
    def __init__(self, cmd: commands.ProcessInference):
        self.job_repository = cmd.job_repository
        self.job_id = cmd.job_id
        self.output_bucket = cmd.s3_bucket_name
        self.key = cmd.key
        self.inference_stat_processor = cmd.inference_stat_processor
        self.job = self.job_repository.get_job_by_id(self.job_id)

    @property
    def inference_file_key(self):
        return f"{self.key}/{self.inference_file_name}"

    def handle(self):
        logger.info(f"Handling process inference for {self.job_id}")
        self.job.job_status = JobStatus.INFERENCE_COMPLETE
        self.process_inference_stats()
        self.job_repository.save(self.job)
        logger.info(f"Completed process inference processing for {self.job_id}")
        return self.job

    def process_inference_stats(self):
        self.job.rdfox_statistics_raw = self.inference_stat_processor.inference_stats
        self.job.rdfox_statistics = self.inference_stat_processor.process_inference()

    def _process_inference_stats(self, stats_text: str):
        return self.inference_stat_processor.process_inference(stats_text=stats_text)
