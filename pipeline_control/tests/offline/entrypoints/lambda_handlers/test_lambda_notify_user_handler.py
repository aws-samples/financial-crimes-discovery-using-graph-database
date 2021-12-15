# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import moto
import pytest

from pipeline_control.entrypoints import lambda_entry_points


class TestNotifyUserHandler:
    def test_1_notify_users(
        self,
        entrypoint_fake_notify_user_handler,
    ):
        lambda_entry_points.handle_notify_user({}, {})
        entrypoint_fake_notify_user_handler.assert_called_once()
