# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pytest

from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
    NeptuneMode,
    NeptuneParallelism,
)


@pytest.fixture
def g_job_configurations_neptune_configuration():
    configuration = NeptuneBulkloaderConfiguration(
        cluster_endpoint=pytest.TEST_NEPTUNE_ENDPOINT,
        source_format="turtle",
        iam_role=pytest.TEST_IAM_ROLE,
        region="ap-southeast-1",
        mode=NeptuneMode.AUTO,
        parallelism=NeptuneParallelism.OVERSUBSCRIBE,
        update_single_cardinality_properties=True,
        queue_request=True,
        fail_on_error=False,
        source="s3://doesntmatter/for/testing/data",
    )
    yield configuration


@pytest.fixture(params=[True, False])
def g_job_configurations_small_rdfox_job_configuration(
    request,
    g_job_configurations_neptune_configuration,
):
    job_configuration = RDFoxJobConfiguration(
        job_id=pytest.TEST_JOB_ID,
        job_key=pytest.TEST_KEY,
        job_bucket=pytest.TEST_BUCKET_NAME,
        output_bucket=pytest.TEST_RESULT_BUCKET,
        requested_cores=4,
        requested_memory=2048,
        init_container_image="1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/pre-rdfox:latest",
        publisher_container_image="1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/post-rdfox:latest",
        rdfox_container_image="1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/custom-rdfox:latest",
        rdfox_init_container_image="oxfordsemantic/rdfox-init",
        auto_shutdown=False,
        license_secret_name="license",
        parallelism=1,
        namespace="ns-rdfox",
        service_account="rdfox-service-account",
        rdfox_port=12110,
        rdfox_password_secret="rdfox-password",
        restart_policy="Never",
        neptune_configuration=g_job_configurations_neptune_configuration,
    )
    if not request.param:
        job_configuration.neptune_configuration = None
    yield job_configuration
