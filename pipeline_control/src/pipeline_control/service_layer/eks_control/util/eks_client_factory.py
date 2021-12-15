# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import tempfile
from datetime import datetime, timedelta
from typing import Optional

import boto3
import kubernetes.client
from awscli.customizations.eks.get_token import (
    TOKEN_EXPIRATION_MINS,
    STSClientFactory,
    TokenGenerator,
)
from botocore import session


class KubernetesClientFactory:
    def __init__(self, cluster_name: str):
        work_session = session.get_session()
        self._client_factory = STSClientFactory(work_session)
        self._cluster_name = cluster_name

        self._last_written_cert_file_location = None

    def get_expiration_time(self):
        token_expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINS)
        return token_expiration.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_client(self) -> kubernetes.client.ApiClient:
        token = self.get_token()["status"]["token"]
        configuration = kubernetes.client.Configuration()
        configuration.api_key["authorization"] = f"{token}"
        configuration.api_key_prefix = {"authorization": "Bearer"}
        configuration.host = self.get_host()
        configuration.verify_ssl = True
        self._write_ca_in_base64()
        configuration.ssl_ca_cert = self._last_written_cert_file_location
        return kubernetes.client.ApiClient(configuration)

    def _write_ca_in_base64(self, cert_encoded: Optional[str] = None):
        if not cert_encoded:
            cert_encoded = self.get_ca()
        cert_decoded = base64.b64decode(cert_encoded)
        tmp_file_name = self._get_temporarily_file_location()
        with open(tmp_file_name, mode="wb") as data:
            data.write(cert_decoded)
            self._last_written_cert_file_location = data.name

    def _get_temporarily_file_location(self):
        with tempfile.NamedTemporaryFile(mode="wb") as data:
            return data.name

    def _describe_cluster(self):
        return boto3.client("eks").describe_cluster(name=self._cluster_name)

    def get_host(self) -> str:
        return self._describe_cluster()["cluster"]["endpoint"]

    def get_ca(self) -> str:
        return self._describe_cluster()["cluster"]["certificateAuthority"]["data"]

    def get_token(self) -> dict:
        sts_client = self._client_factory.get_sts_client()
        token = TokenGenerator(sts_client).get_token(self._cluster_name)
        # token = TokenGenerator(self._client).get_token(self._cluster_name)
        return {
            "kind": "ExecCredential",
            "apiVersion": "client.authentication.k8s.io/v1alpha1",
            "spec": {},
            "status": {
                "expirationTimestamp": self.get_expiration_time(),
                "token": token,
            },
        }

    def __eq__(self, other):
        return type(self) == type(other) and self._cluster_name == other._cluster_name
