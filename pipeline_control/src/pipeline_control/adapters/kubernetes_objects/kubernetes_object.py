# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from abc import abstractmethod
from typing import Optional

import kubernetes.client
from hikaru.generate import get_yaml
from hikaru.meta import HikaruDocumentBase
from hikaru.model.rel_1_18.v1.v1 import PodSecurityContext, ResourceRequirements

logger = logging.getLogger(__name__)


class KubernetesObject:
    def __init__(self, client: kubernetes.client.ApiClient, namespace: str):
        self.client = client
        self.namespace = namespace
        self._kubernetes_object: Optional[HikaruDocumentBase] = None

    def deploy(self):
        resource = self._to_hikaru()
        resource.set_client(self.client)
        kubernetes_object = resource.create(namespace=self.namespace)
        self._kubernetes_object = kubernetes_object

    """
    securityContext:
    runAsNonRoot: true
    runAsUser: <User id>
    fsGroup: <group id>
    fsGroupChangePolicy: "OnRootMismatch"
    """

    def make_security_context(self):
        security_context = PodSecurityContext(
            fsGroup=1211,
            runAsNonRoot=True,
            runAsUser=1211,
            runAsGroup=1211,
            fsGroupChangePolicy="OnRootMismatch",
        )
        return security_context

    def _make_main_container_resource_requirements(self):
        return ResourceRequirements(
            requests={
                "memory": self.job_configuration.requested_memory,
                "cpu": self.job_configuration.requested_cores,
            },
            limits={
                "memory": self.job_configuration.requested_memory,
                "cpu": self.job_configuration.requested_cores,
            },
        )

    @property
    def kubernetes_object(self):
        if not self._kubernetes_object:
            raise Exception("Not created yet")
        return self._kubernetes_object

    @abstractmethod
    def _to_hikaru(self):
        raise Exception("Not implemented")

    def __repr__(self):
        kubernetes_object = self._to_hikaru()
        return get_yaml(kubernetes_object)

    def __str__(self):
        return self.__repr__()
