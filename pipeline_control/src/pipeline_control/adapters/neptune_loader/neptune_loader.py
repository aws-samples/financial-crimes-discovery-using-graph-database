# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from dataclasses import dataclass

import neptune_load.bulk_loader.bulk_loader
from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
)

logger = logging.getLogger(__name__)


@dataclass
class NeptuneLoader:
    neptune_load_configuration: NeptuneBulkloaderConfiguration
    signer: SigV4Signer
    _bulk_loader = None
    neptune_load_id = None

    @property
    def bulk_loader(self):
        if not self._bulk_loader:
            configuration = self.neptune_load_configuration
            self._bulk_loader = neptune_load.bulk_loader.bulk_loader.BulkLoader(
                source=configuration.source,
                neptune_endpoint=configuration.cluster_endpoint,
                signer=self.signer,
                iam_role_arn=configuration.iam_role,
                source_format=configuration.source_format,
                update_single_cardinality_properties=configuration.update_single_cardinality_properties,
                queueRequest=configuration.queue_request,
                region=configuration.region,
                parallelism=configuration.parallelism.value,
            )
        return self._bulk_loader

    @bulk_loader.setter
    def bulk_loader(self, load_id: str):
        self.bulk_loader.load_id = load_id

    @property
    def load_id(self):
        return self._bulk_loader.load_id

    def initiate_bulk_load(self):
        self.bulk_loader.initiate_bulk_load_from_s3()
        return self.bulk_loader.load_id

    def cancel_load(self):
        self.bulk_loader.cancel_load()

    def get_status(self):
        self.bulk_loader._refresh_status()
        return self.bulk_loader.status
