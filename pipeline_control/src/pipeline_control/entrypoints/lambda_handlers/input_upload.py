# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import pipeline_control.domain.commands
import pipeline_control.service_layer.handlers.new_job_handler
from app_config import AppConfig
from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.entrypoints.util.file_upload_fiter import make_validate_file_name
from pipeline_control.entrypoints.util.s3_upload_event import S3Uploadevent
from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)

logger = logging.getLogger(__name__)


def parse_object_key(object_key: str):
    file_name = object_key.split("/")[-1]
    data_prefix = object_key.split("/")[:-1]
    data_prefix = ("/").join(data_prefix)
    return (file_name, data_prefix)


def handle_input_upload(event, app_config: AppConfig):
    target_jobspec_name = app_config.jobspec_name
    target_cluster = app_config.cluster_name
    s3_event: S3Uploadevent = S3Uploadevent.from_json(event)
    bucket_name = s3_event.bucket_name
    object_key = s3_event.object_key
    (file_name, _) = parse_object_key(object_key=object_key)
    make_validate_file_name(target_file_name=target_jobspec_name)(file_name)

    new_job_command = pipeline_control.domain.commands.CreateNewJob(
        s3_bucket_name=bucket_name,
        key=object_key,
        job_repository=JobRepository(),
        job_configuration_name=target_jobspec_name,
        api_client_factory=KubernetesClientFactory(cluster_name=target_cluster),
    )
    new_job_handler = (
        pipeline_control.service_layer.handlers.new_job_handler.NewJobHandler(
            cmd=new_job_command
        )
    )
    return new_job_handler.handle()
