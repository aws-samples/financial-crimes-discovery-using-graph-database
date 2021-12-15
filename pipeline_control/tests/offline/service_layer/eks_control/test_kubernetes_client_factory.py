# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from unittest import mock

import boto3
import pytest
from pyexpect import expect

from pipeline_control.service_layer.eks_control.util.eks_client_factory import (
    KubernetesClientFactory,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestKubernetesClientFactory:
    @pytest.fixture
    def eks_client_under_test(self, fake_eks_cluster):
        return KubernetesClientFactory(pytest.TEST_CLUSTER_NAME)

    def test_1_get_eks_token(self, eks_client_under_test, fake_eks_cluster):
        boto3.client("eks")
        token = eks_client_under_test.get_token()
        expect(token["status"]["token"]).to.exist()

    @mock.patch(
        "pipeline_control.service_layer.eks_control.util.eks_client_factory.KubernetesClientFactory.get_ca",
        autospec=True,
    )
    def test_2_get_eks_client(
        self, patched_ca, eks_client_under_test, fake_eks_cluster
    ):

        patched_ca.return_value = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUN5RENDQWJDZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1EWXlNekEwTXpBek9Gb1hEVE14TURZeU1UQTBNekF6T0Zvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTFIrCjhOMms1UkdBaUZsQjJsWDQ3b3ArSnUwMmZqcVVIRVRwSVZCaGdhUGJMMldpaC9jeDNqTkEvbGdRd2VVa2FoN3cKWUVxRkhRMC8ybXA1a2xWaUJkaC93TVJTS0RkRFpxUkdEWC9jeTZaYXh2UjdDT1Nubm1kMERnYkRXVkxWNFdyZAppZ1pmd1NHOWxaQXlyTy9VdXIvS1ZRNk5OVk1yNGQ1WURiem1JWEtVQjh2c2h0MDJpV05KSFZhL2VRaXBOaWY2CmtNbVlsUUpCbFAzNVZOUGpwbFluYjByWlQxenB1THBzdDRmRExVanlLdGRVbVpkRGpEUzJadHoyak9kT1VwTDgKc1Y1WitrSlVISUpCbXZOV21TMTRCRnZGM0ZacGxMKzM2c0lyK21MV3ZtSkhGWTA2L1V4U0xvWEwvblBuQ3BrVQpWSjJ0RlhXUnVQQ2NiZllwRzNVQ0F3RUFBYU1qTUNFd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dFQkFDaFRQTGF6eDVhYmFYWE5jRTk2b0h5RVdqMGcKWWZTZzBqM05rU2RiQTcxamZyOHZBWVp1N0RmYjFEei9yUm5jcXA1T2lBdHlBLzl6UGpqOXl6VUxJS0l0Y1hVYQpudEJ1UVJ4WHhFV0owR0FwZS8yR2dhYW5Yc3pYNk9peTVvM0s5YmJoSFhEV0JEVFJaZy9JdWs1QWZTaExzSXlCCjkwTkk5bXhOUEdvenJIRVY3Y0lXNFpLTisvNmQ0bDVsMHZFT3Q2K29Zc0ZUMnI0QXZIbVhTam05d2NpcmFKZFEKalJCcnkrMGZTOEpFWDNJZ2szb29TSzRiaVl3bk5TOEEzbjAxc3pjY2pCNkFxODdUSkN0aUc0YVB4TktkM3RhYQoweCs0VmM1RWlHc1Y4MGhybTVza2FCeDl5T3FNOVFNM0pnd0FYWWM5Znl2ZG8xZFRLek03VWwwbGdXMD0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="
        client = boto3.client("eks")
        print(fake_eks_cluster)
        client = eks_client_under_test.get_client()

        patched_ca.assert_called_once()
        expect(client.configuration.api_key).to.exist()
        expect(client.configuration.api_key["authorization"]).to.exist()
        expect(client.configuration.api_key_prefix).to.equal(
            {"authorization": "Bearer"}
        )
        expect(client.configuration.ssl_ca_cert).to.exist()
        expect(client.configuration.ssl_ca_cert).to.contain("/tmp")
        with open(client.configuration.ssl_ca_cert, "r") as data:
            cert_text = data.read()
            expect(cert_text).to.contain("-----BEGIN CERTIFICATE-----")
            expect(cert_text).to.contain("-----END CERTIFICATE-----")
        expect(client.configuration.host).contains(".eks.amazonaws.com")
