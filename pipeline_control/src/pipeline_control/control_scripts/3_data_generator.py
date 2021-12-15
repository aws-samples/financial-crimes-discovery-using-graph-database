# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import os
import tempfile

import boto3
import click
from hikaru.model.rel_1_18.v1.v1 import Job

from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.control_scripts.util import monitor_job_container
from pipeline_control.domain.commands import CreateNewJob
from pipeline_control.service_layer.eks_control.job_control import JobControl
from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)
from pipeline_control.service_layer.handlers.data_generator_job_handler import (
    NewDGJobHandler,
)

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)

logger = logging.getLogger("data_generator")
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()

CURRENT_ACCOUNT = boto3.client("sts").get_caller_identity()["Account"]
my_session = boto3.session.Session()
my_region = my_session.region_name


JOB_TEMPLATE = {
    "requested_cores": 3,
    "requested_memory": "3Gi",
    "data_generator_container_image": f"{CURRENT_ACCOUNT}.dkr.ecr.{my_region}.amazonaws.com/data-generator:latest",
    "parallelism": 1,
    "job_bucket": "CHANGE-ME",
    "data_path": "CHANGE-ME",
    "number_of_messages": 10000,
    "number_of_files": 50,
    "number_of_parties": 1000,
    "max_days_before": 3,
    "chain_days_range": 3,
    "thread_count": 70,
}


def upload_jobspec(requested_cores, requested_memory, data_set, bucket, parties):
    job_spec = create_jobspec(
        requested_cores=requested_cores,
        requested_memory=requested_memory,
        job_key=data_set,
        bucket=bucket,
    )

    deploy_jobspec(
        job_spec=job_spec,
        bucket=bucket,
        key=data_set,
    )


def create_jobspec(
    requested_cores: int,
    requested_memory: int,
    parties: int,
    transactions: int,
    job_key: str,
    bucket: str,
    thread_count: int,
    max_days_before: int,
    chain_days_range: int,
):
    template = JOB_TEMPLATE.copy()
    template["requested_cores"] = requested_cores
    template["requested_memory"] = f"{requested_memory}Gi"
    template["job_key"] = job_key
    template["job_bucket"] = bucket
    template["number_of_messages"] = transactions
    template["number_of_parties"] = parties
    template["data_path"] = job_key
    template["thread_count"] = thread_count
    template["max_days_before"] = max_days_before
    template["chain_days_range"] = chain_days_range
    return template


def deploy_jobspec(job_spec, bucket, key):
    _, path = tempfile.mkstemp()
    try:
        with open(path, "wb") as data:
            data.write(bytes(json.dumps(job_spec), "utf-8"))
            logger.debug(f"Spec written to {path}")
        _upload_jobspec_to_s3(bucket=bucket, key=key, temp_path=path)
    finally:
        os.remove(path)


def _upload_jobspec_to_s3(bucket, key, temp_path):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket)
    with open(temp_path, "rb") as data:
        logger.info(f"Uploading {temp_path} to s3://{bucket}/{key}")
        bucket.upload_fileobj(data, key)


def schedue_job(bucket, data_set, job_configuration_name, kubernetes_cluster):
    factory = KubernetesClientFactory(kubernetes_cluster)
    repository = JobRepository()
    repository.create_table_if_not_exists()

    new_job_command = CreateNewJob(
        s3_bucket_name=bucket,
        key=data_set,
        job_repository=repository,
        job_configuration_name=job_configuration_name,
        api_client_factory=factory,
    )

    handler = NewDGJobHandler(cmd=new_job_command)
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


@click.command()
@click.option("--cores", default=3)
@click.option("--memory", default=2)
@click.option("--parties", default=1000)
@click.option("--thread-count", default=70)
@click.option("--chain-days-range", default=3)
@click.option("--max-days-before", default=3)
@click.option("--transactions", default=10000)
@click.option("--data-set")
@click.option("--kubernetes-cluster")
@click.option("--bucket")
def go(
    data_set,
    parties,
    transactions,
    cores,
    memory,
    bucket,
    kubernetes_cluster,
    chain_days_range,
    thread_count,
    max_days_before,
):
    job_spec = create_jobspec(
        requested_cores=cores,
        requested_memory=memory,
        parties=parties,
        transactions=transactions,
        job_key=data_set,
        bucket=bucket,
        chain_days_range=chain_days_range,
        thread_count=thread_count,
        max_days_before=max_days_before,
    )

    jobspec_name = f"data_generator_{transactions}T-{parties}P.jobspec.json"
    jobspec_key = f"{data_set}/{jobspec_name}"

    deploy_jobspec(
        job_spec=job_spec,
        bucket=bucket,
        key=jobspec_key,
    )

    schedue_job(
        bucket=bucket,
        data_set=data_set,
        job_configuration_name=jobspec_name,
        kubernetes_cluster=kubernetes_cluster,
    )


if __name__ == "__main__":
    go()
