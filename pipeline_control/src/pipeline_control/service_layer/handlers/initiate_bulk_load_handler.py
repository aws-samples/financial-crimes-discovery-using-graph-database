# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from pipeline_control.domain import commands
from pipeline_control.domain.model import JobStatus
from pipeline_control.service_layer.handlers import util
from pipeline_control.service_layer.handlers.handler import Handler

logger = logging.getLogger(__name__)


class InitiateBulkloadHandler(Handler):
    def __init__(self, cmd: commands.ProcessInference):
        self.job_repository = cmd.job_repository
        self.neptune_loader_factory = cmd.neptune_loader_factory
        self.job_id = cmd.job_id
        self.job = self.job_repository.get_job_by_id(self.job_id)
        self.source = cmd.source

    def handle(self):
        self._update_job_config()
        self._initiate_bulk_load()
        return self.job

    def _update_job_config(self):
        job_neptune_configuration = self.job.job_configuration.neptune_configuration
        if not job_neptune_configuration:
            job_neptune_configuration = util.neptune_config_from_app_config()
        job_neptune_configuration.source = self.source
        self.job.job_configuration.neptune_configuration = job_neptune_configuration

    def _initiate_bulk_load(self):
        neptune_loader = self.neptune_loader_factory.make_loader(
            override_neptune_load_configuration=self.job.job_configuration.neptune_configuration
        )
        logger.info(f"Beginnging bulk load for {self.job.job_id}")
        neptune_writer_instance = util.neptune_instance_type_from_endpoint(
            neptune_loader.neptune_load_configuration.cluster_endpoint
        )
        self.job.neptune_writer_instance = neptune_writer_instance
        neptune_loader.initiate_bulk_load()
        self.job.job_configuration.neptune_configuration = (
            neptune_loader.neptune_load_configuration
        )
        self.job.neptune_load_id = neptune_loader.load_id
        load_id = neptune_loader.load_id
        logger.info(f"Bulk load for {self.job_id} initiated load_id {load_id}")
        self.job.job_status = JobStatus.NEPTUNE_LOAD_IN_PROGRESS
        self.job.neptune_load_id = load_id
        self.job_repository.save(self.job)
