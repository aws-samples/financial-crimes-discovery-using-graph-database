# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from dataclasses import dataclass

import click
from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

import pipeline_control.domain.model
from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
)
from pipeline_control.adapters.neptune_loader.neptune_loader_factory import (
    NeptuneLoaderFactory,
)
from pipeline_control.domain.commands import InitiateBulkload
from pipeline_control.service_layer.handlers.initiate_bulk_load_handler import (
    InitiateBulkloadHandler,
)

logger = logging.getLogger("bulk_loader")
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(formatter)


@dataclass
class BulkloadJobCreator:
    job_repository: JobRepository = JobRepository()

    def create_load_job(
        self, key, job_configuration
    ) -> pipeline_control.domain.model.Job:
        job = pipeline_control.domain.model.Job(
            key=key, job_configuration=job_configuration
        )
        self.job_repository.save(job)
        return job

    def create_job_configuration(self, neptune_configuration):
        job_configuration = RDFoxJobConfiguration()
        job_configuration.neptune_configuration = neptune_configuration
        return job_configuration

    def cancel_load(
        self,
        load_id,
        **kwargs,
    ):
        neptune_loader_factory = NeptuneLoaderFactory(
            neptune_load_configuration=None,
            signer=SigV4Signer(),
        )

        cancel_loader = neptune_loader_factory.make_read_only_loader(
            neptune_load_id=load_id,
        )
        cancel_loader.cancel_load()

    def submit_job(
        self,
        **kwargs,
    ):
        neptune_configuration = NeptuneBulkloaderConfiguration.from_dict(kwargs)
        job_configuration = self.create_job_configuration(
            neptune_configuration=neptune_configuration
        )
        key = self.derive_key(kwargs["source"])
        job = self.create_load_job(job_configuration=job_configuration, key=key)
        neptune_loader_factory = NeptuneLoaderFactory(
            neptune_load_configuration=neptune_configuration,
            signer=SigV4Signer(),
        )
        job_repository = JobRepository()
        initate_bulk_load_command = InitiateBulkload(
            source=neptune_configuration.source,
            neptune_loader_factory=neptune_loader_factory,
            job_repository=job_repository,
            job_id=job.job_id,
        )
        bulk_load_handler = InitiateBulkloadHandler(cmd=initate_bulk_load_command)
        bulk_load_handler.handle()
        job.neptune_load_id
        # self.monitor_job(neptune_load_id)

    def derive_key(self, source):
        key_parts = source[5:]
        dynamic = key_parts.replace("_", "-")
        res = f"BULKLOAD-ONLY-FROM-{dynamic}"
        return res


@click.command()
@click.option("--cancel_load")
@click.option("--source")
@click.option("--cluster_endpoint")
@click.option("--source_format", default="ntriples")
@click.option("--iam_role", default="arn:aws:iam::1234567891011:role/NeptuneLoaderRole")
@click.option("--region", default="ap-southeast-1")
@click.option("--mode", default="AUTO")
@click.option("--fail_on_error", default=False)
@click.option("--parallelism", default="OVERSUBSCRIBE")
@click.option("--update_single_cardinality_properties", default=True)
@click.option("--queue_request", default=True)
@click.option("--named_graph", default="TEST")
def go(
    cancel_load,
    source,
    source_format,
    cluster_endpoint,
    iam_role,
    region,
    mode,
    fail_on_error,
    parallelism,
    update_single_cardinality_properties,
    queue_request,
    named_graph,
):
    submitter = BulkloadJobCreator()

    logger.info(
        f"Requested {source}, {source_format}, {cluster_endpoint} {iam_role}, {region}, {mode}, {fail_on_error}, {parallelism}, {update_single_cardinality_properties}, {queue_request}, {named_graph}"
    )

    if cancel_load:
        logger.info(f"Requested cancellation of {cancel_load}")
        submitter.cancel_load(
            load_id=cancel_load,
            cluster_endpoint=cluster_endpoint,
            region=region,
        )
    else:
        submitter.submit_job(
            cluster_endpoint=cluster_endpoint,
            source_format=source_format,
            source=source,
            iam_role=iam_role,
            region=region,
            mode=mode,
            fail_on_error=fail_on_error,
            parallelism=parallelism,
            update_single_cardinality_properties=update_single_cardinality_properties,
            queue_request=queue_request,
            named_graph=named_graph,
        )


if __name__ == "__main__":
    go()
