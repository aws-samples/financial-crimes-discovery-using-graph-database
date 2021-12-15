# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NeptuneMode(Enum):
    AUTO = "AUTO"
    RESUME = "RESUE"


class NeptuneParallelism(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    OVERSUBSCRIBE = "OVERSUBSCRIBE"


@dataclass
class NeptuneBulkloaderConfiguration:
    cluster_endpoint: str
    source_format: str
    source: str
    iam_role: str
    region: str
    mode: NeptuneMode
    fail_on_error: bool
    parallelism: NeptuneParallelism
    update_single_cardinality_properties: bool
    queue_request: bool
    named_graph: Optional[str] = None

    def __and__(self, other):
        merged_config = self.__dict__
        if other and type(other) == NeptuneBulkloaderConfiguration:
            other_dict = other.__dict__
            merged_config.update(other_dict)
        return NeptuneBulkloaderConfiguration(**merged_config)

    @classmethod
    def from_dict(cls, the_dict):
        parallelism_raw = the_dict["parallelism"]
        mode_raw = the_dict["mode"]
        if "." in parallelism_raw:
            parallelism_raw = parallelism_raw.split(".")[1]
        if "." in mode_raw:
            mode_raw = mode_raw.split(".")[1]
        the_dict["parallelism"] = NeptuneParallelism(parallelism_raw)
        the_dict["mode"] = NeptuneMode(mode_raw)
        return cls(**the_dict)

    @property
    def json(self):
        as_dict = self.__dict__
        as_dict["parallelism"] = self.parallelism.value
        as_dict["mode"] = self.mode.value
        return as_dict

    def __rep__(self):
        return self.json
