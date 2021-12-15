# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

import pipeline_control.service_layer.handlers.notify_user_handler
import pipeline_control.service_layer.handlers.refresh_bulkload_handler
from app_config import AppConfig
from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.neptune_loader.neptune_loader_factory import (
    NeptuneLoaderFactory,
)
from pipeline_control.adapters.notifier.sns_notifier import SNSNotifier
from pipeline_control.domain import commands
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStatProcessor,
)

logger = logging.getLogger(__name__)


class WrongEventTypeException(Exception):
    def __init__(self, event_type):
        self.type = event_type
        super().__init__("Wrong event type")


def handle_refresh_bulkload(event, app_config: AppConfig):
    if not event["detail-type"] == "Scheduled Event":
        raise WrongEventTypeException(event["detail-type"])

    job_respository = JobRepository()
    neptune_stat_processor = NeptuneStatProcessor()
    neptune_loader_factory = NeptuneLoaderFactory(
        signer=SigV4Signer(),
        neptune_load_configuration=None,
    )

    refresh_bulkload_command = commands.RefreshBulkload(
        job_repository=job_respository,
        neptune_stat_processor=neptune_stat_processor,
        neptune_loader_factory=neptune_loader_factory,
    )

    handler = pipeline_control.service_layer.handlers.refresh_bulkload_handler.RefreshBulkloadHandler(
        cmd=refresh_bulkload_command
    )
    return handler.handle()


def handle_notification(event, app_config: AppConfig):
    job_repository = JobRepository()

    sns_notifier = SNSNotifier(
        topic_arn=app_config.bulkload_topic,
    )

    notify_user_command = commands.NotifyUser(
        notifier=sns_notifier,
        job_repository=job_repository,
    )

    handler = (
        pipeline_control.service_layer.handlers.notify_user_handler.NotifyUserHandler(
            cmd=notify_user_command
        )
    )
    handler.handle()
