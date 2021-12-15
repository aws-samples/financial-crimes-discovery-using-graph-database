# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import moto

from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)


@moto.mock_eks
@moto.mock_sts
class FakeKubernetesClientFactory(KubernetesClientFactory):
    pass
