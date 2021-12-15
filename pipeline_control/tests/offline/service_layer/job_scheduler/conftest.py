# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pytest


@pytest.fixture
def a_rdfox_job(job_scheduler_under_test):
    return job_scheduler_under_test.create_new_job()
