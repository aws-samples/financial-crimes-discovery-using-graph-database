# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pytest
from pyexpect import expect

from pipeline_control.adapters.neptune_loader.neptune_loader import NeptuneLoader


class TestNeptuneLoader:
    @pytest.mark.usefixtures("mocked_bulk_loader")
    def test_1_can_initiate_load(self, neptune_loader_under_test):
        load_id = neptune_loader_under_test.initiate_bulk_load()
        expect(load_id).to.equal(pytest.TEST_NEPTUNE_LOAD_ID)

    @pytest.mark.usefixtures("mocked_bulk_loader")
    def test_2_can_get_load_status(self, neptune_loader_under_test, load_success_text):
        load_status = neptune_loader_under_test.get_status()
        expect(load_status.raw).to.equal(load_success_text)
