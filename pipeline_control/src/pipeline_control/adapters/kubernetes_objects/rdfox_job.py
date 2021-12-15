# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

import kubernetes.client
from hikaru.generate import get_yaml
from hikaru.model.rel_1_18.v1.v1 import (
    Container,
    ContainerPort,
    EmptyDirVolumeSource,
    EnvVar,
    EnvVarSource,
    Job,
    JobSpec,
    ObjectMeta,
    PodSpec,
    PodTemplateSpec,
    SecretKeySelector,
    SecretVolumeSource,
    Volume,
    VolumeMount,
)

import app_config
from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
)

from .kubernetes_object import KubernetesObject

logger = logging.getLogger(__name__)


@dataclass
class RDFoxJobConfiguration:
    job_bucket: str = "because_repos_dont_care"
    job_key: str = "about this"
    job_id: str = None
    output_bucket: str = "output"
    requested_cores: int = 4
    requested_memory: str = "2Gi"
    data_path: Optional[str] = ""
    data_generator_container_image: Optional[str] = ""
    number_of_messages: Optional[int] = 100
    number_of_parties: Optional[int] = 10000
    max_days_before: Optional[int] = 3
    chain_days_range: Optional[int] = 3
    number_of_files: Optional[int] = 100
    thread_count: Optional[int] = 20
    init_container_image: str = (
        "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/pre-rdfox:latest"
    )
    publisher_container_image: str = (
        "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/post-rdfox:latest"
    )
    rdfox_container_image: str = (
        "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/custom-rdfox:latest"
    )
    rdfox_init_container_image: str = "oxfordsemantic/rdfox-init"
    license_secret_name: str = "rdfox-license"
    auto_shutdown: str = False
    namespace: str = "ns-rdfox"
    service_account: str = "rdfox-service-account"
    rdfox_port: int = 12110
    rdfox_password_secret: str = "rdfox-password"
    restart_policy: str = "Never"
    parallelism: int = 1
    neptune_configuration: Optional[NeptuneBulkloaderConfiguration] = None

    @classmethod
    def from_dict(cls, the_dict):
        if "neptune_configuration" in the_dict:
            neptune_configuration_dict = the_dict["neptune_configuration"]
            if neptune_configuration_dict:
                neptune_configuration = NeptuneBulkloaderConfiguration.from_dict(
                    neptune_configuration_dict
                )
                the_dict["neptune_configuration"] = neptune_configuration
        return cls(**the_dict)

    @property
    def json(self):
        object_dict = vars(self)
        if "neptune_configuration" in object_dict:
            neptune_configuration = object_dict["neptune_configuration"]
            if neptune_configuration:
                object_dict["neptune_configuration"] = neptune_configuration.json
        return object_dict


class RDFoxJob(KubernetesObject):
    def __init__(
        self,
        job_configuration: RDFoxJobConfiguration,
        client: kubernetes.client.ApiClient = None,
    ):
        super().__init__(client=client, namespace=job_configuration.namespace)
        self.job_configuration = job_configuration
        self.job_id = None

    def _to_hikaru(self):
        # Emergency break do not try this at home
        if self.job_configuration.job_id is None:
            raise Exception(
                "This job configuration needs a job id to function - set it manually for now. Will fix it later"
            )
        return self.make_job()

    def make_job(self) -> Job:
        pod_spec = self._make_job_pod_spec()
        pod_template_spec = self._make_job_template_spec(pod_spec=pod_spec)
        job_spec = self._make_job_spec(pod_template_spec=pod_template_spec)
        metadata = self._make_metadata()
        kubernetes_job = Job(metadata=metadata, spec=job_spec)
        logger.debug(
            f"""Synthesised job spec
        {get_yaml(kubernetes_job)}
        ===============
        """
        )
        return kubernetes_job

    def _make_metadata(self) -> ObjectMeta:
        return ObjectMeta(generateName="rdfox")

    def _make_job_spec(self, pod_template_spec) -> JobSpec:
        return JobSpec(
            parallelism=self.job_configuration.parallelism,
            template=pod_template_spec,
        )

    def _make_job_template_spec(self, pod_spec) -> PodTemplateSpec:
        labels = {"app": "rdfox"}
        if self.job_configuration.auto_shutdown is False:
            labels["rdfoxexpose"] = "aye"
        metadata = ObjectMeta(labels=labels)
        return PodTemplateSpec(spec=pod_spec, metadata=metadata)

    def _make_job_pod_spec(self) -> PodSpec:
        rdfox_data_volume = self._make_temp_volume("rdfox-data")
        config_volume = self._make_temp_volume("config")
        data_volume = self._make_temp_volume("data-data")
        output_volume = self._make_temp_volume("output-data")
        license_volume = Volume(
            name="rdfox-license",
            secret=SecretVolumeSource(
                secretName=self.job_configuration.license_secret_name
            ),
        )

        volumes = [
            rdfox_data_volume,
            config_volume,
            data_volume,
            output_volume,
            license_volume,
        ]

        rdfox_volume_mounts = self._make_rdfox_volume_mounts(
            data_volume=data_volume,
            config_volume=config_volume,
            output_volume=output_volume,
            rdfox_data_volume=rdfox_data_volume,
        )

        init_volume_mounts = self._make_init_volume_mounts(
            data_volume=data_volume,
            config_volume=config_volume,
            output_volume=output_volume,
        )

        init_container = self._make_init_container(volume_mounts=init_volume_mounts)

        rdfox_license_loader_container = self._make_rdfox_license_loader_container(
            rdfox_data_volume=rdfox_data_volume,
            license_volume=license_volume,
        )

        rdfox_container = self._make_rdfox_container(volume_mounts=rdfox_volume_mounts)

        publisher_container = self._make_publisher_container(
            output_volume=output_volume, config_volume=config_volume
        )

        job_pod_template_spec = PodSpec(
            containers=[rdfox_container, publisher_container],
            initContainers=[
                init_container,
                rdfox_license_loader_container,
                # rdfox_init_container,
            ],
            securityContext=self.make_security_context(),
            volumes=volumes,
            serviceAccountName=self.job_configuration.service_account,
            restartPolicy=self.job_configuration.restart_policy,
        )

        return job_pod_template_spec

    def _make_rdfox_container(
        self,
        volume_mounts,
    ) -> Container:

        container = Container(
            name="rdfox-container",
            imagePullPolicy="Always",
            image=self.job_configuration.rdfox_container_image,
            resources=self._make_main_container_resource_requirements(),
            volumeMounts=volume_mounts,
            env=self._make_env() + self._make_rdfox_envs(),
            ports=[
                ContainerPort(
                    containerPort=self.job_configuration.rdfox_port, protocol="TCP"
                )
            ],
            # livenessProbe=Probe(
            #    failureThreshold=3,
            #    httpGet=HTTPGetAction(
            #        path="/health",
            #        port=self.job_configuration.rdfox_port,
            #        scheme="HTTP",
            #    ),
            #    initialDelaySeconds=3600,
            #    periodSeconds=3,
            #    successThreshold=1,
            #    timeoutSeconds=1,
            # ),
        )

        return container

    def _make_rdfox_license_loader_container(
        self,
        rdfox_data_volume: Volume,
        license_volume: Volume,
    ):
        rdfox_data_mount = VolumeMount(
            name=rdfox_data_volume.name, mountPath="/home/rdfox/.RDFox", readOnly=False
        )
        license_mount = VolumeMount(
            name=license_volume.name,
            mountPath="/home/rdfox/license",
            readOnly=True,
        )

        container = Container(
            name="rdfox-license-loader",
            imagePullPolicy="IfNotPresent",
            image="ubuntu:latest",
            volumeMounts=[
                rdfox_data_mount,
                license_mount,
            ],
            command=["/bin/sh"],
            args=[
                "-c",
                "echo 'copying the license where it can be seen' && cp /home/rdfox/license/RDFox.lic /home/rdfox/.RDFox && ls -la /home/rdfox/.RDFox",
            ],
        )

        return container

    def _make_rdfox_init_container(
        self,
        volume_mounts: List[VolumeMount],
    ) -> Container:

        container = Container(
            name="rdfox-init-container",
            imagePullPolicy="Always",
            # lifecycle=lifecycle,
            image=self.job_configuration.rdfox_init_container_image,
            # resources=self._make_rdfox_resource_requirements(),
            volumeMounts=volume_mounts,
            # args=["-persist-roles", "off", "-persist-ds", "off", "daemon"],
            env=self._make_env() + self._make_rdfox_envs(),
        )

        return container

    def _make_rdfox_envs(self):
        return [
            EnvVar(name="RDFOX_ROLE", value="ADMIN"),
            EnvVar(
                name="RDFOX_PASSWORD",
                valueFrom=EnvVarSource(
                    secretKeyRef=SecretKeySelector(
                        name=self.job_configuration.rdfox_password_secret,
                        key="password",
                    )
                ),
            ),
        ]

    def _make_init_volume_mounts(
        self,
        data_volume,
        config_volume,
        output_volume,
    ):
        data_mount = VolumeMount(
            name=data_volume.name, mountPath="/data", readOnly=False
        )
        config_mount = VolumeMount(
            name=config_volume.name, mountPath="/scripts", readOnly=False
        )
        output_mount = VolumeMount(
            name=output_volume.name, mountPath="/output", readOnly=False
        )

        return [
            data_mount,
            config_mount,
            output_mount,
        ]

    def _make_rdfox_volume_mounts(
        self,
        rdfox_data_volume,
        data_volume,
        config_volume,
        output_volume,
    ):
        rdfox_data_mount = VolumeMount(
            name=rdfox_data_volume.name, mountPath="/home/rdfox/.RDFox", readOnly=False
        )
        data_mount = VolumeMount(
            name=data_volume.name, mountPath="/data", readOnly=True
        )
        config_mount = VolumeMount(
            name=config_volume.name, mountPath="/scripts", readOnly=True
        )
        output_mount = VolumeMount(
            name=output_volume.name, mountPath="/output", readOnly=False
        )

        return [
            rdfox_data_mount,
            data_mount,
            config_mount,
            output_mount,
        ]

    def _make_init_container(self, volume_mounts: List[VolumeMount]) -> Container:

        container = Container(
            imagePullPolicy="Always",
            name="init-container",
            image=self.job_configuration.init_container_image,
            # command=[
            #    "sh",
            #    "-c",
            #    "echo Init is running! && sleep 10 && echo init finished",
            # ],
            # args=["-c", "echo Init is running"]
            # resources=self._make_rdfox_resource_requirements(),
            volumeMounts=volume_mounts,
            env=self._make_env() + [],
        )

        return container

    def _make_publisher_container(
        self, output_volume: Volume, config_volume: Volume
    ) -> Container:
        output_mount = VolumeMount(
            name=output_volume.name, mountPath="/output", readOnly=False
        )
        config_mount = VolumeMount(
            name=config_volume.name, mountPath="/scripts", readOnly=False
        )

        container = Container(
            imagePullPolicy="Always",
            name="publisher-container",
            image=self.job_configuration.publisher_container_image,
            volumeMounts=[output_mount, config_mount],
            env=self._make_env(
                override={
                    "BUCKET_NAME": f"{self.job_configuration.output_bucket}",
                    "DATA_PATH": f"{self._data_path_from_job_id(self.job_configuration.job_id)}",
                }
            ),
        )

        return container

    def _default_env(self, override):

        default_env = {
            "JOB_ID": f"{self.job_configuration.job_id}",
            "AUTO_SHUTDOWN": f"{self.job_configuration.auto_shutdown}",
            "BUCKET_NAME": f"{self.job_configuration.job_bucket}",
            "DATA_PATH": f"{self._data_path_from_job_id(self.job_configuration.job_id)}",
            "NUMBER_OF_CORES": f"{self.job_configuration.requested_cores}",
        }

        if override:
            default_env.update(override)

        return default_env

    def _make_env(self, override=None):
        env_vars = []
        envs = self._default_env(override)
        for key, value in envs.items():
            env_vars.append(EnvVar(name=key, value=value))
        return env_vars

    def _make_temp_volume(self, name) -> Volume:
        return Volume(name=name, emptyDir=EmptyDirVolumeSource())

    def _data_path_from_job_id(self, job_id: str):
        return job_id.split(app_config.app_configuration.job_id_delimeter)[0]
