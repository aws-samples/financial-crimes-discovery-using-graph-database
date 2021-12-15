# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import neptune_load

from .neptune_loader import NeptuneLoader


@dataclass
class FakeNeptuneLoader(NeptuneLoader):
    fake_load_id: str = "lala"
    complete_after_iterations: Optional[int] = 10
    success_stats: Optional[dict] = field(default_factory=dict)
    load_stats: Optional[dict] = field(default_factory=dict)
    failure_stats: Optional[dict] = field(default_factory=dict)
    cluster_endpoint: str = ""
    iam_role_arn: str = ""
    source_format: str = ""
    source: str = ""
    signer: str = ""
    succeed: bool = True

    @property
    def load_id(self):
        if self._load_id:
            return self._load_id
        raise Exception("No load id until we've started loading")

    def initiate_bulk_load(self):
        self._iterations = 0
        self._start = datetime.now()
        self._load_id = self.fake_load_id
        return self.load_id

    def get_status(self):
        if self._iterations is None:
            raise Exception("Not loading yet")
        if not (self._iterations >= self.complete_after_iterations):
            self._iterations = self._iterations + 1
            return self.wrapped_load_stats

        if self.succeed:
            return self.wrapped_success_stats
        else:
            return self.wrapped_failure_stats

    @property
    def wrapped_success_stats(self):
        return self.wrap(self.success_stats)

    @property
    def wrapped_load_stats(self):
        return self.wrap(self.load_stats)

    def wrap(self, stats):
        return neptune_load.bulk_loader.bulk_loader.BulkloadStatus.create_from_api_response_text(
            json.dumps(stats)
        )
