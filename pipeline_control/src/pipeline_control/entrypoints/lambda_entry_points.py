# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import app_config
import pipeline_control.entrypoints.lambda_handlers.input_upload
import pipeline_control.entrypoints.lambda_handlers.process_inference
import pipeline_control.entrypoints.lambda_handlers.refresh_bulkload
from pipeline_control.entrypoints.lambda_handlers.refresh_bulkload import (
    WrongEventTypeException,
)
from pipeline_control.entrypoints.util.file_upload_fiter import WrongFileException

config: app_config.AppConfig = app_config.app_configuration

logger = logging.getLogger("pipeline_control")


def handle_refresh_bulkload(event, context={}):
    logger.info("handle_refresh_bulkload called")
    logger.debug(f"Event:{event}")
    try:
        status = pipeline_control.entrypoints.lambda_handlers.refresh_bulkload.handle_refresh_bulkload(
            event, config
        )
        # Skimping on Lambda Functions for now will factor this out in the future
        handle_notify_user(event, context)
        return status
    except WrongEventTypeException as wete:
        return f"Not a relevant type {wete.type}"


def handle_notify_user(event, context={}):
    pipeline_control.entrypoints.lambda_handlers.refresh_bulkload.handle_notification(
        event, config
    )


def handle_input_upload(event, context={}):
    logger.info("handle_input_upload called")
    logger.debug(f"Event:{event}")
    return_job = None
    try:
        return_job = pipeline_control.entrypoints.lambda_handlers.input_upload.handle_input_upload(
            event, config
        )
    except WrongFileException as wfe:
        logger.debug(f"This is not the file we were looking for {wfe}")
        return None

    return return_job.job_id


def handle_process_inference(event, context={}):
    logger.info("handle_process_inference called")
    logger.debug(f"Event:{event}")
    return_job = pipeline_control.entrypoints.lambda_handlers.process_inference.handle_process_inference(
        event, config
    )
    return_job = pipeline_control.entrypoints.lambda_handlers.process_inference.handle_initiate_bulkload(
        event, config
    )
    return return_job.neptune_load_id
