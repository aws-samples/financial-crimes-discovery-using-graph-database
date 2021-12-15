# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass
from typing import Optional

from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer

from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
)
from pipeline_control.service_layer.handlers import util

from .neptune_loader import NeptuneLoader


@dataclass
class NeptuneLoaderFactory:
    neptune_load_configuration: Optional[NeptuneBulkloaderConfiguration]
    signer: SigV4Signer

    def make_read_only_loader(
        self,
        neptune_load_id: str,
        override_neptune_load_configuration: Optional[
            NeptuneBulkloaderConfiguration
        ] = None,
    ):
        neptune_configuration = self.resolve_neptune_configuration(
            override_neptune_load_configuration
        )
        if not neptune_configuration.source:
            neptune_configuration.source = "s3://loader/only/data"
        loader = NeptuneLoader(
            signer=self.signer,
            neptune_load_configuration=neptune_configuration,
        )
        loader.bulk_loader = neptune_load_id
        return loader

    def make_loader(
        self,
        override_neptune_load_configuration: Optional[
            NeptuneBulkloaderConfiguration
        ] = None,
    ):
        neptune_configuration = self.resolve_neptune_configuration(
            override_neptune_load_configuration
        )
        return NeptuneLoader(
            neptune_load_configuration=neptune_configuration, signer=self.signer
        )

    def resolve_neptune_configuration(self, override) -> NeptuneBulkloaderConfiguration:
        neptune_configuration = util.neptune_config_from_app_config()
        neptune_configuration = neptune_configuration & self.neptune_load_configuration
        neptune_configuration = neptune_configuration & override
        return neptune_configuration
