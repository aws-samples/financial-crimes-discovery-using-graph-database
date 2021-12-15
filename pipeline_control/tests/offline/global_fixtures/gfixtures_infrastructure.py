# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import moto
import pytest

from pipeline_control.adapters.job_repository.fake_job_repository import (
    FakeJobRepository,
)
from pipeline_control.service_layer.eks_control.util.fake_eks_client_factory import (
    FakeKubernetesClientFactory,
)


@pytest.fixture
def mocked_repository():
    job_repository_for_test = FakeJobRepository()
    job_repository_for_test.create_table_if_not_exists()
    yield job_repository_for_test
    job_repository_for_test.delete_table()


@pytest.fixture
def fake_eks_cluster():
    with moto.mock_eks():
        client = boto3.client("eks")
        cluster = client.create_cluster(
            name=pytest.TEST_CLUSTER_NAME,
            roleArn=pytest.TEST_IAM_ROLE,
            resourcesVpcConfig={},
        )
        yield cluster
        client.delete_cluster(name=pytest.TEST_CLUSTER_NAME)


@moto.mock_sts
@moto.mock_eks
@pytest.fixture
def g_infrastructure_fake_kubernetes_client_factory(fake_eks_cluster):
    client_factory = FakeKubernetesClientFactory(cluster_name=pytest.TEST_CLUSTER_NAME)
    return client_factory


@moto.mock_sts
@moto.mock_eks
@pytest.fixture
def fake_kubernetes_client(g_infrastructure_fake_kubernetes_client_factory):
    return g_infrastructure_fake_kubernetes_client_factory.get_client()
