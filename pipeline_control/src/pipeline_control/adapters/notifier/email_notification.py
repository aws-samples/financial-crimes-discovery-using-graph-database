# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import abc
from dataclasses import dataclass


@dataclass
class EmailNotification(abc.ABC):
    @property
    @abc.abstractmethod
    def subject(self):
        return self._get_subject

    @property
    @abc.abstractmethod
    def message(self):
        return self._get_subject

    def to_email(self):
        return {
            "Message": self.message,
            "Subject": self.subject,
        }
