# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from datetime import datetime

import pytest
from pyexpect import expect

from pipeline_control.domain.model import JobStatus


class TestNotificationHandler:
    def test_1_notification_content(
        self,
        mocked_repository,
        completed_job,
        notify_user_handler_under_test,
        g_neptune_load_complete,
    ):
        notification_content = notify_user_handler_under_test.make_notification(
            completed_job
        )
        expect(notification_content.partial_chains_amount).equals(1337)
        expect(notification_content.load_errors).equals([])
        expect(notification_content.job_updated.day).equals(
            datetime.strptime(pytest.TEST_FROZE_DATE, "%Y-%M-%d").day
        )

    def test_2_notification_sent(
        self,
        mocked_repository,
        completed_job,
        notify_user_handler_under_test,
        g_neptune_load_complete,
        mocked_sns_notifier,
    ):
        notify_user_handler_under_test.handle()
        retrieved_job = mocked_repository.get_job_by_id(completed_job.job_id)
        expect(retrieved_job.job_status).equals(JobStatus.SUCCESS_NOTIFICATION_SENT)
        mocked_sns_notifier.send_message.assert_called_once()
