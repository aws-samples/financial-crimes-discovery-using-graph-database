# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from hikaru.model.rel_1_18.v1.v1 import Job

from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.control_scripts.util import monitor_job_container
from pipeline_control.domain.commands import CreateNewJob
from pipeline_control.service_layer.eks_control.job_control import JobControl
from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)
from pipeline_control.service_layer.handlers.new_job_handler import NewJobHandler

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)

logger = logging.getLogger("test")
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()

if __name__ == "__main__":
    factory = KubernetesClientFactory("eks_cluster2")
    repository = JobRepository()
    repository.create_table_if_not_exists()
    new_job_command = CreateNewJob(
        s3_bucket_name="INPUT_BUCKET",
        key="2021-01-01/2021-01-01_90cores_500Gi.rdfoxjob.json",
        job_repository=repository,
        job_configuration_name="lal",
        api_client_factory=factory,
    )

    handler = NewJobHandler(cmd=new_job_command)
    job = handler.handle()
    logger.info(f"Job created {job.kubernetes_name} {job.job_status}")
    job_controller = JobControl(api_client_factory=factory)
    namespace = job.job_configuration.namespace
    the_job = Job().read(
        client=factory.get_client(),
        name=job.kubernetes_name,
        namespace=namespace,
    )

    while True:
        try:
            monitor_job_container(factory=factory, job=job, namespace=namespace)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received - shutting down")
            job_controller.delete_job_and_its_pods(the_job)
            break
        except Exception as e:
            logger.critical("Something broke - cleaning up")
            job_controller.delete_job_and_its_pods(the_job)
            raise e
