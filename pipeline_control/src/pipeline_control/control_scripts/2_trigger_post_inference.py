# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

from pipeline_control.adapters.job_repository.job_repository import JobRepository
from pipeline_control.adapters.neptune_loader.neptune_loader import NeptuneLoader
from pipeline_control.domain.commands import ProcessInference
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStatProcessor,
)
from pipeline_control.service_layer.handlers.process_inference_handler import (
    ProcessInferenceHandler,
)

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)


if __name__ == "__main__":
    THE_KEY = "2021-01-01/2021-01-01_2021-08-04_028/rdfox.log"
    THE_FORMAT = "turtle"
    THE_JOB_ID = "2021-01-01_2021-07-26_026"
    repository = JobRepository()
    key = "2021-01-01"
    job_id = THE_JOB_ID
    s3_bucket_name = "OUTPUT_BUCKET"
    # neptune_endpoint = "localhost"
    neptune_endpoint = (
        "neptune.cluster-czgutmoafmkn.ap-southeast-1.neptune.amazonaws.com:8182"
    )
    iam_role_arn = "arn:aws:iam::1234567891011:role/NeptuneLoaderRole"
    prefix = f"{key}/{job_id}"
    # loader_source = f"s3://{s3_bucket_name}/{prefix}/"
    # loader_source = f"s3://{s3_bucket_name}/much_nicer"
    loader_source = f"s3://{s3_bucket_name}/{THE_KEY}"

    neptune_loader = NeptuneLoader(
        signer=SigV4Signer(),
        iam_role=iam_role_arn,
        source=loader_source,
        source_format=THE_FORMAT,
        neptune_endpoint=neptune_endpoint,
    )
    process_inference_command = ProcessInference(
        job_id=job_id,
        s3_bucket_name=s3_bucket_name,
        key=THE_KEY,
        job_repository=repository,
        neptune_loader=neptune_loader,
        inference_stat_processor=InferenceStatProcessor(""),
    )

    handler = ProcessInferenceHandler(cmd=process_inference_command)
    handler.handle()

    # Here comes the hacks
    bulk_loader = neptune_loader._bulk_loader
    load_id = bulk_loader.load_id

    try:
        while True:
            logger.info(
                f"================ Start of Iteration {load_id} ===================="
            )
            bulk_loader._refresh_status()
            status = bulk_loader.status
            logger.info(status.raw)
            logger.info("================ End of Iteration ====================")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received - shutting down")
