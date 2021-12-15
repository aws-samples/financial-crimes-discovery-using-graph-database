# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest

import moto

from pipeline_control.entrypoints import lambda_entry_points


@moto.mock_sts
class TestRefreshBulkloadLambdaHandler:
    def test_1_invoke_refresh_bulkload_if_time_based(
        self,
        entrypoint_fake_refresh_bulkload_command,
        entrypoint_fake_refresh_bulkload_handler,
        entrypoint_time_based_event,
        entrypoint_fake_notify_user_handler,
    ):
        lambda_entry_points.handle_refresh_bulkload(entrypoint_time_based_event, {})
        entrypoint_fake_refresh_bulkload_command.assert_called_with(
            job_repository=unittest.mock.ANY,
            neptune_stat_processor=unittest.mock.ANY,
            neptune_loader_factory=unittest.mock.ANY,
        )
        entrypoint_fake_refresh_bulkload_handler.assert_called_once()

    def test_2_dontinvoke_refresh_bulkload_if_not_time_based(
        self,
        entrypoint_fake_refresh_bulkload_handler,
        entrypoint_not_time_based_event,
        entrypoint_fake_notify_user_handler,
    ):
        lambda_entry_points.handle_refresh_bulkload(entrypoint_not_time_based_event, {})
        entrypoint_fake_refresh_bulkload_handler.handle.assert_not_called()
