# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass
from typing import Optional

from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.neptune_loader.neptune_loader_factory import (
    NeptuneLoaderFactory,
)
from pipeline_control.adapters.notifier.sns_notifier import SNSNotifier
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStatProcessor,
)
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStatProcessor,
)
from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)


class Command:
    pass


@dataclass
class ProcessInference(Command):
    s3_bucket_name: str
    key: str
    job_repository: JobRepository
    job_id: str
    inference_stat_processor: Optional[InferenceStatProcessor] = None


@dataclass
class InitiateBulkload(Command):
    job_repository: JobRepository
    neptune_loader_factory: NeptuneLoaderFactory
    source: str
    job_id: str


@dataclass
class CreateNewJob(Command):
    s3_bucket_name: str
    key: str
    job_repository: JobRepository
    job_configuration_name: str
    api_client_factory: KubernetesClientFactory


@dataclass
class RefreshBulkload(Command):
    job_repository: JobRepository
    neptune_loader_factory: NeptuneLoaderFactory
    neptune_stat_processor: NeptuneStatProcessor


@dataclass
class NotifyUser(Command):
    job_repository: JobRepository
    notifier: SNSNotifier
