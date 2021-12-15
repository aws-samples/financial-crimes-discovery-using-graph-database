# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass, field
from typing import Optional

from pipeline_control.adapters.neptune_loader.fake_neptune_loader import (
    FakeNeptuneLoader,
)
from pipeline_control.adapters.neptune_loader.neptune_loader import NeptuneLoader
from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
)

from .neptune_loader_factory import NeptuneLoaderFactory


@dataclass
class FakeNeptuneLoaderFactory(NeptuneLoaderFactory):
    fake_loader: NeptuneLoader = None
    fake_load_id: str = "lala"
    complete_after_iterations: Optional[int] = 10
    success_stats: Optional[dict] = field(default_factory=dict)
    load_stats: Optional[dict] = field(default_factory=dict)
    failure_stats: Optional[dict] = field(default_factory=dict)
    iam_role_arn: str = ""
    source_format: str = ""
    source: str = ""
    signer: str = ""
    succeed: bool = True

    def make_loader(
        self,
        override_neptune_load_configuration: Optional[
            NeptuneBulkloaderConfiguration
        ] = None,
    ):
        neptune_configuration = self.resolve_neptune_configuration(
            override_neptune_load_configuration
        )
        if not self.fake_loader:
            self.fake_loader = FakeNeptuneLoader(
                fake_load_id=self.fake_load_id,
                complete_after_iterations=self.complete_after_iterations,
                load_stats=self.load_stats,
                success_stats=self.success_stats,
                neptune_load_configuration=neptune_configuration,
            )
            self.fake_loader.initiate_bulk_load()
        return self.fake_loader

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
        if not self.fake_loader:
            self.fake_loader = FakeNeptuneLoader(
                fake_load_id=neptune_load_id,
                complete_after_iterations=self.complete_after_iterations,
                load_stats=self.load_stats,
                success_stats=self.success_stats,
                neptune_load_configuration=neptune_configuration,
            )
            self.fake_loader.initiate_bulk_load()
        return self.fake_loader

    # this is not safe and I'm not proud of it but we only exist for testing so TODO:
    def set_loading(self):
        if self.fake_loader:
            self.fake_loader._iterations = self.complete_after_iterations - 1

    def set_complete(self):
        if self.fake_loader:
            self.fake_loader._iterations = self.complete_after_iterations
