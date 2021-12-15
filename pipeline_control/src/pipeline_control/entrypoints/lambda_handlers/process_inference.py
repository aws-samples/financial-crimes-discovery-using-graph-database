# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

import pipeline_control.domain.commands
import pipeline_control.service_layer.handlers.initiate_bulk_load_handler
import pipeline_control.service_layer.handlers.new_job_handler
import pipeline_control.service_layer.handlers.process_inference_handler
from app_config import AppConfig
from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.neptune_loader.neptune_loader_factory import (
    NeptuneLoaderFactory,
)
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStatProcessor,
)
from pipeline_control.entrypoints.util.file_upload_fiter import make_validate_file_name
from pipeline_control.entrypoints.util.s3_upload_event import S3Uploadevent
from pipeline_control.service_layer.s3_json_loader import S3JsonLoader

logger = logging.getLogger(__name__)


def handle_process_inference(event, app_config: AppConfig):
    target_rdfoxlog_name = app_config.rdfoxlog_name
    file_name_validator = make_validate_file_name(target_file_name=target_rdfoxlog_name)
    s3_event: S3Uploadevent = S3Uploadevent.from_json(event)
    bucket_name = s3_event.bucket_name
    object_key = s3_event.object_key
    job_repository = JobRepository()

    (job_id, file_name, data_prefix) = parse_object_key(object_key=object_key)
    file_name_validator(file_name)
    inference_stats = S3JsonLoader.download_from_s3(
        bucket_name=bucket_name,
        key=object_key,
    )
    inference_stat_processor = InferenceStatProcessor(inference_stats=inference_stats)
    process_inference_command = pipeline_control.domain.commands.ProcessInference(
        s3_bucket_name=bucket_name,
        key=data_prefix,
        job_repository=job_repository,
        job_id=job_id,
        inference_stat_processor=inference_stat_processor,
    )
    process_inference_handler = pipeline_control.service_layer.handlers.process_inference_handler.ProcessInferenceHandler(
        cmd=process_inference_command
    )
    return process_inference_handler.handle()


def handle_initiate_bulkload(event, app_config: AppConfig):
    s3_event: S3Uploadevent = S3Uploadevent.from_json(event)
    bucket_name = s3_event.bucket_name
    object_key = s3_event.object_key
    job_repository = JobRepository()
    (job_id, _, data_prefix) = parse_object_key(object_key=object_key)
    neptune_source = f"s3://{bucket_name}/{data_prefix}/data/"

    neptune_loader_factory = NeptuneLoaderFactory(
        signer=SigV4Signer(),
        neptune_load_configuration=None,
    )

    initiate_bulk_load_command = pipeline_control.domain.commands.InitiateBulkload(
        source=neptune_source,
        neptune_loader_factory=neptune_loader_factory,
        job_id=job_id,
        job_repository=job_repository,
    )

    initiate_bulk_load_handler = pipeline_control.service_layer.handlers.initiate_bulk_load_handler.InitiateBulkloadHandler(
        cmd=initiate_bulk_load_command
    )
    return initiate_bulk_load_handler.handle()


# Based on s3://terraform-somebucketname/2021-01-01/2021-01-01_2021-07-19_081/rdfox.log
# [-1] = filename, [-2] = job_id
def parse_object_key(object_key: str):
    key_split = object_key.split("/")
    file_name = key_split[-1]
    data_prefix = key_split[:-1]
    job_id = key_split[-2]
    data_prefix = ("/").join(data_prefix)
    return (job_id, file_name, data_prefix)
