# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from unittest.mock import create_autospec

import pytest
from kubernetes.client import ApiClient

from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJob


@pytest.fixture
def friendly_client():
    friendly_mock = create_autospec(ApiClient)
    return friendly_mock


@pytest.fixture
def rdfox_job_under_test(
    friendly_client, g_job_configurations_small_rdfox_job_configuration
):
    job = RDFoxJob(job_configuration=g_job_configurations_small_rdfox_job_configuration)
    return job


@pytest.fixture
def rdfox_volume_mounts(rdfox_job_under_test):
    vol_1 = rdfox_job_under_test._make_temp_volume("one")
    vol_2 = rdfox_job_under_test._make_temp_volume("two")
    vol_3 = rdfox_job_under_test._make_temp_volume("three")
    vol_4 = rdfox_job_under_test._make_temp_volume("four")
    return [vol_1, vol_2, vol_3, vol_4]


@pytest.fixture
def rdfox_container_under_test(rdfox_job_under_test, rdfox_volume_mounts):
    test_container = rdfox_job_under_test._make_rdfox_container(rdfox_volume_mounts)
    return test_container


@pytest.fixture
def rdfox_init_container_under_test(rdfox_job_under_test, rdfox_volume_mounts):
    test_container = rdfox_job_under_test._make_rdfox_init_container(
        volume_mounts=rdfox_volume_mounts
    )
    return test_container


@pytest.fixture
def init_container_under_test(rdfox_job_under_test):
    vol_1 = rdfox_job_under_test._make_temp_volume("one")
    vol_2 = rdfox_job_under_test._make_temp_volume("two")
    test_container = rdfox_job_under_test._make_init_container(
        volume_mounts=[vol_1, vol_2],
    )
    return test_container


@pytest.fixture
def publisher_container_under_test(rdfox_job_under_test):
    vol_1 = rdfox_job_under_test._make_temp_volume("one")
    vol_2 = rdfox_job_under_test._make_temp_volume("two")
    test_container = rdfox_job_under_test._make_publisher_container(
        output_volume=vol_1,
        config_volume=vol_2,
    )
    return test_container


@pytest.fixture
def job_pod_spec_under_test(rdfox_job_under_test):
    return rdfox_job_under_test._make_job_pod_spec()


@pytest.fixture
def job_pod_template_spec_under_test(rdfox_job_under_test, job_pod_spec_under_test):
    return rdfox_job_under_test._make_job_template_spec(
        pod_spec=job_pod_spec_under_test
    )


@pytest.fixture
def job_spec_under_test(rdfox_job_under_test, job_pod_template_spec_under_test):
    return rdfox_job_under_test._make_job_spec(
        pod_template_spec=job_pod_template_spec_under_test
    )


@pytest.fixture
def job_under_test(rdfox_job_under_test):
    return rdfox_job_under_test.make_job()
