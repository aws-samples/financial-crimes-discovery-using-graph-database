# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

import app_config
from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.neptune_loader.neptune_loader_factory import (
    NeptuneLoaderFactory,
)
from pipeline_control.domain.commands import RefreshBulkload
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStatProcessor,
)
from pipeline_control.service_layer.handlers.refresh_bulkload_handler import (
    RefreshBulkloadHandler,
)

logger = logging.getLogger("test_run")
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()

if __name__ == "__main__":
    app_config = app_config.app_configuration
    repository = JobRepository()
    repository.create_table_if_not_exists()
    neptune_loader_factory = NeptuneLoaderFactory(
        signer=SigV4Signer(),
        neptune_load_configuration=None,
    )
    neptune_stat_processor = NeptuneStatProcessor()

    command = RefreshBulkload(
        job_repository=repository,
        neptune_loader_factory=neptune_loader_factory,
        neptune_stat_processor=neptune_stat_processor,
    )

    handler = RefreshBulkloadHandler(cmd=command)

    handler.handle()
