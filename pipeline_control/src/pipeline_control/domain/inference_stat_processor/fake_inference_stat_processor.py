# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass

from .inference_stat_processor import InferenceStatProcessor, InferenceStats


@dataclass
class FakeInferenceStatProcessor(InferenceStatProcessor):
    def process_inference(self):
        return InferenceStats()
