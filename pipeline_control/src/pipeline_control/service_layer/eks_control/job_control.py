# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import kubernetes
from hikaru.model.rel_1_18.v1.v1 import Job, Pod

from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)

logger = logging.getLogger(__name__)


class JobControl:
    def __init__(
        self,
        api_client_factory: KubernetesClientFactory = None,
    ):
        self.api_client_factory = api_client_factory

    def get_job_logs(self, kubernetes_job: Job):
        pod = self.get_pod_by_job(kubernetes_job)
        return self.get_pod_logs(pod)

    def get_pod_by_job(self, kubernetes_job: Job, api_client=None):
        if not api_client:
            api_client = self.api_client_factory.get_client()
        api_instance = kubernetes.client.CoreV1Api(api_client)
        namespace = kubernetes_job.metadata.namespace
        api_response = api_instance.list_namespaced_pod(
            namespace, label_selector=f"job-name={kubernetes_job.metadata.name}"
        )

        the_pod = Pod().read(
            client=api_client,
            namespace=namespace,
            name=api_response.items[0].metadata.name,
        )
        return the_pod

    def get_pod_logs(self, pod: Pod):
        api_client = self.api_client_factory.get_client()
        logs = {}
        containers = pod.spec.containers + pod.spec.initContainers
        for container in containers:
            these_logs = []
            try:
                container_logs = pod.readNamespacedPodLog(
                    pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    container=container.name,
                    client=api_client,
                    pretty="true",
                )
                these_logs = container_logs.obj
            except Exception as e:
                logger.info(e)
            logs[container.name] = these_logs
        return logs

    def delete_job_and_its_pods(self, job: Job):
        api_client = self.api_client_factory.get_client()
        the_pod = self.get_pod_by_job(job)
        namespace = job.metadata.namespace
        logger.info(f"Deleting job {job.metadata.name}")
        job.delete(client=api_client, name=job.metadata.name, namespace=namespace)
        logger.info(f"Deleting pod {the_pod.metadata.name}")
        the_pod.delete(
            client=api_client,
            name=the_pod.metadata.name,
            namespace=namespace,
        )
