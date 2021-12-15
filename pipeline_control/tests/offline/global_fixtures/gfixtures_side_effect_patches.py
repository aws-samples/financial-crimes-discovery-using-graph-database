# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from unittest.mock import Mock, patch

import boto3
import hikaru
import moto
import pytest

from pipeline_control.service_layer.job_scheduler.rdfoxjob_scheduler import (
    RDFoxJobScheduler,
)


@pytest.fixture
def job_scheduler_under_test(
    mocked_repository,
    g_job_configurations_small_rdfox_job_configuration,
    fake_kubernetes_client,
):
    scheduler = RDFoxJobScheduler(
        job_repository=mocked_repository,
        api_client=fake_kubernetes_client,
        job_configuration=g_job_configurations_small_rdfox_job_configuration,
    )
    return scheduler


@pytest.fixture
def mocked_hikaru_create(job_scheduler_under_test):
    with patch("hikaru.model.rel_1_18.v1.v1.Job.create", autospec=True) as hikaru_patch:
        test_name = "glumanda"
        dummyJob = hikaru.model.rel_1_18.v1.v1.Job()
        dummyMeta = hikaru.model.rel_1_18.v1.v1.ObjectMeta()
        dummyMeta.name = test_name
        dummyMeta.namespace = "ns-rdfox"
        dummyJob.metadata = dummyMeta
        dummy_spec = job_scheduler_under_test.create_kubernetes_job().make_job()
        dummyJob.merge(dummy_spec, overwrite=False)
        hikaru_patch.return_value = dummyJob
        yield test_name


@pytest.fixture
def mocked_hikaru_read(job_scheduler_under_test, fake_ec2):
    with patch("hikaru.model.rel_1_18.v1.v1.Pod.read", autospec=True) as hikaru_patch:
        test_name = "glumanda"
        dummyPod = hikaru.model.rel_1_18.v1.v1.Pod()
        dummyMeta = hikaru.model.rel_1_18.v1.v1.ObjectMeta()
        dummyMeta.name = test_name
        dummyMeta.namespace = "ns-rdfox"
        dummyPod.metadata = dummyMeta
        dummySpec = hikaru.model.rel_1_18.v1.v1.PodSpec(containers=[])
        dummySpec.nodeName = fake_ec2
        dummyPod.spec = dummySpec
        hikaru_patch.return_value = dummyPod
        yield test_name


@pytest.fixture
def mocked_pod_read(job_scheduler_under_test):
    with patch(
        "kubernetes.client.CoreV1Api.list_namespaced_pod", autospec=True
    ) as kc_mock:
        mocked_structure = Mock()
        meta_mock = Mock()
        meta_mock.metadata.name = "lala"
        mocked_structure.items = [meta_mock]
        kc_mock.return_value = mocked_structure
        yield kc_mock


@pytest.fixture
def fake_ec2():
    with moto.mock_ec2() as mock_ec2:
        ec2_client = boto3.client("ec2")
        ec2 = boto3.resource("ec2")
        images = ec2_client.describe_images()
        instances = ec2.create_instances(
            MaxCount=1,
            MinCount=1,
            InstanceType=pytest.TEST_WORKER_NODE_TYPE,
            ImageId=images["Images"][0]["ImageId"],
        )
        yield instances[0].private_dns_name
