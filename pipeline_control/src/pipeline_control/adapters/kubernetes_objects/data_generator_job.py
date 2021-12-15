# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from dataclasses import dataclass

import kubernetes.client
from hikaru.model.rel_1_18.v1.v1 import (
    Container,
    EmptyDirVolumeSource,
    EnvVar,
    Job,
    JobSpec,
    ObjectMeta,
    PodSpec,
    PodTemplateSpec,
    Volume,
    VolumeMount,
)

import app_config

from .kubernetes_object import KubernetesObject

logger = logging.getLogger(__name__)


@dataclass
class DataGeneratorJobConfiguration:
    job_bucket: str = "because_repos_dont_care"
    data_path: str = "10M3DAY"
    job_key: str = "about this"
    job_id: str = None
    output_bucket: str = "output"
    requested_cores: int = 4
    requested_memory: int = 2048
    data_generator_container_image: str = (
        "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/data-generator:latest"
    )
    auto_shutdown: bool = False
    parallelism: int = 1
    namespace: str = "ns-rdfox"
    service_account: str = "rdfox-service-account"
    restart_policy: str = "Never"

    # Generation config
    number_of_messages: int = 10000000
    number_of_parties: int = 10000
    number_of_files: int = int(requested_cores)
    max_days_before: int = 3
    chain_days_range: int = 3
    thread_count: int = 20

    @classmethod
    def from_dict(cls, the_dict):
        return cls(**the_dict)

    @classmethod
    def from_json(cls, object_dict):
        return cls(**object_dict)

    @property
    def json(self):
        object_dict = vars(self)
        return object_dict


class DataGeneratorJob(KubernetesObject):
    def __init__(
        self,
        job_configuration: DataGeneratorJobConfiguration,
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
        # logger.info(
        #     f"""Today we are making
        # {get_yaml(kubernetes_job)}
        # ===============
        # """
        # )
        return kubernetes_job

    def _make_metadata(self) -> ObjectMeta:
        return ObjectMeta(generateName="datagenerator")

    def _make_job_spec(self, pod_template_spec) -> JobSpec:
        return JobSpec(
            parallelism=self.job_configuration.parallelism,
            template=pod_template_spec,
        )

    def _make_job_template_spec(self, pod_spec) -> PodTemplateSpec:
        return PodTemplateSpec(spec=pod_spec)

    def _make_job_pod_spec(self) -> PodSpec:
        data_volume = self._make_temp_volume("data-data")

        volumes = [data_volume]

        data_generator_container = self._make_data_generator_container(
            data_volume=data_volume
        )

        job_pod_template_spec = PodSpec(
            containers=[data_generator_container],
            initContainers=[],
            volumes=volumes,
            serviceAccountName=self.job_configuration.service_account,
            restartPolicy=self.job_configuration.restart_policy,
        )

        return job_pod_template_spec

    def _make_data_generator_container(self, data_volume: Volume) -> Container:

        data_mount = VolumeMount(
            name=data_volume.name, mountPath="/data", readOnly=False
        )

        container = Container(
            imagePullPolicy="Always",
            name="data-generator-container",
            image=self.job_configuration.data_generator_container_image,
            resources=self._make_main_container_resource_requirements(),
            volumeMounts=[data_mount],
            env=self._make_env(
                override={
                    "BUCKET_NAME": f"{self.job_configuration.job_bucket}",
                    "DATA_PATH": f"{self.job_configuration.data_path}",
                    "NUM_OF_FILES": f"{self.job_configuration.number_of_files}",
                    "NUM_OF_MSG": f"{self.job_configuration.number_of_messages}",
                    "NUM_OF_PARTIES": f"{self.job_configuration.number_of_parties}",
                    "MAX_DAYS_BEFORE": f"{self.job_configuration.max_days_before}",
                    "CHAIN_DAYS_RANGE": f"{self.job_configuration.chain_days_range}",
                    "THREAD_COUNT": f"{self.job_configuration.thread_count}",
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
        return Volume(name=name, emptyDir=EmptyDirVolumeSource(medium="Memory"))

    def _data_path_from_job_id(self, job_id: str):
        return job_id.split(app_config.app_configuration.job_id_delimeter)[0]
