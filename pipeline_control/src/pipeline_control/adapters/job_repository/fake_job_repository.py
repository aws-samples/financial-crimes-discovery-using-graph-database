# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import moto

from pipeline_control.adapters.job_repository.job_repository import JobRepository


@moto.mock_dynamodb2
class FakeJobRepository(JobRepository):
    def __init__(self):
        super().__init__()
