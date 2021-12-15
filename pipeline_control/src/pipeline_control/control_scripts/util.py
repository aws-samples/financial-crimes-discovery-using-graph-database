# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import time

from hikaru.model.rel_1_18.v1.v1 import Job

from pipeline_control.service_layer.eks_control.job_control import JobControl

logger = logging.getLogger(__name__)


def monitor_job_container(factory, job, namespace):
    job_controller = JobControl(api_client_factory=factory)
    logger.info(
        "=========================== NEXT ITERATION ========================================================"
    )
    the_job = Job().read(
        client=factory.get_client(),
        name=job.kubernetes_name,
        namespace=namespace,
    )
    pod_logs = job_controller.get_job_logs(the_job)
    for container_name, container_logs in pod_logs.items():
        logger.info("================ Logs for {container_name} ================")
        logger.info(container_logs)
        logger.info(
            "================ End of Logs for {container_name} ================"
        )
    time.sleep(2)
    logger.info(
        "=========================== END ITERATION ========================================================"
    )
