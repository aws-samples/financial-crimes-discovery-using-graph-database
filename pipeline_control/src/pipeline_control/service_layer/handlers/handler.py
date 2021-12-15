# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import abc


class Handler(abc.ABC):
    @abc.abstractmethod
    def handle(self):
        raise NotImplementedError()
