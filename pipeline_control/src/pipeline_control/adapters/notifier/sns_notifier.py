# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass

import boto3

from pipeline_control.adapters.notifier.email_notification import EmailNotification


@dataclass
class SNSNotifier:
    topic_arn: str

    @property
    def sns_client(self):
        return boto3.client("sns")

    def send_message(self, email_notification: EmailNotification):
        send_command_dict = {
            "TopicArn": self.topic_arn,
        }
        message_dict = email_notification.to_email()
        send_command_dict.update(message_dict)
        self.sns_client.publish(**send_command_dict)
