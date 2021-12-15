# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import time
from abc import abstractmethod

import kubernetes.client

from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.kubernetes_objects.kubernetes_object import (
    KubernetesObject,
)
from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.domain.model import Job, JobStatus
from pipeline_control.service_layer.eks_control.job_control import JobControl
from pipeline_control.service_layer.handlers import util

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(
        self,
        job_repository: JobRepository,
        api_client: kubernetes.client.ApiClient,
        job_configuration: RDFoxJobConfiguration,
    ):
        self.job_respository = job_repository
        self.api_client = api_client
        self.job_configuration = job_configuration

    def create_new_job(self) -> Job:
        job = Job(
            key=self.job_configuration.job_key,
            job_configuration=self.job_configuration,
        )
        self.job_respository.save(job)
        logger.info(f"Created new job {job.job_id}")
        return job

    def create_and_schedule_new_job(self) -> Job:
        job = self.create_new_job()
        # SUPERHACKY BUT IM RUNNING OUT OF TIME
        self.job_configuration.job_id = job.job_id
        # ========================================
        rdfox_job = self.create_kubernetes_job()
        self.schedule_kubernetes_job(job=job, kubernetes_job=rdfox_job)
        logger.info(f"Scheduled {job.job_id} as {job.kubernetes_name}")
        return job

    def schedule_kubernetes_job(self, job: Job, kubernetes_job: KubernetesObject):
        kubernetes_job.deploy()
        kubernetes_object = kubernetes_job.kubernetes_object
        job.kubernetes_name = kubernetes_object.metadata.name
        job.kubernetes_worker_type = self.try_get_worker_type(kubernetes_object)
        job.job_status = JobStatus.SCHEDULED
        self.job_respository.save(job)

    def try_get_worker_type(self, kubernetes_object):
        instance_type = "Could not identity in time"
        worker_name = self.try_get_worker_name(kubernetes_object)
        if worker_name:
            instance_type_temp = util.ec2_instance_type_from_name(worker_name)
            if instance_type_temp:
                instance_type = instance_type_temp
        return f"{instance_type}:{worker_name}"

    def try_get_worker_name(self, kubernetes_object):
        job_control = JobControl(api_client_factory=None)
        the_pod = None
        max_wait = 10
        pod_wait = 0
        the_node_name = None
        while not the_pod and pod_wait < max_wait:
            the_pod = job_control.get_pod_by_job(
                kubernetes_object, api_client=self.api_client
            )
            if the_pod:
                the_node_name = the_pod.spec.nodeName
            time.sleep(1)
            max_wait = max_wait + 1
        return the_node_name

    @abstractmethod
    def create_kubernetes_job(self) -> Job:
        raise NotImplementedError()
