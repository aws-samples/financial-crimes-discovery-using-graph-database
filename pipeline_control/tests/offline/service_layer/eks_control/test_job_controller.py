# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from unittest.mock import MagicMock, patch

import boto3
import moto
import pytest
from hikaru.model.rel_1_18.v1.v1 import Container, Pod, PodSpec
from hikaru.utils import Response
from pyexpect import expect

from pipeline_control.service_layer.eks_control.job_control import JobControl
from pipeline_control.service_layer.eks_control.util.fake_eks_client_factory import (
    FakeKubernetesClientFactory,
)

TEST_CLUSTER_NAME = "glumanda-cluster"
TEST_ROLE_ARN = "arn:aws:iam::123456789012:role/EKS"


class TestJobControl:
    @pytest.fixture
    def job_monitor_under_test(self, fake_eks_cluster):
        job_monitor = JobControl(
            api_client_factory=FakeKubernetesClientFactory(TEST_CLUSTER_NAME),
        )
        return job_monitor

    def test_1_get_pod_logs(self, job_monitor_under_test, fake_eks_cluster):
        with patch("hikaru.model.rel_1_18.v1.v1.Pod", autospec=True) as faked_pod:
            pod = Pod()
            expected_containers = ["shiggy", "glumanda", "bisasam"]
            pod.spec = PodSpec(
                containers=[
                    Container(name="shiggy"),
                    Container(name="glumanda"),
                    Container(name="bisasam"),
                ]
            )
            pod.readNamespacedPodLog = MagicMock(
                return_value=Response(("a log", "200", "x"), "lah")
            )
            logs = job_monitor_under_test.get_pod_logs(pod)
            for ec in expected_containers:
                expect(logs.keys()).to.contain(ec)
