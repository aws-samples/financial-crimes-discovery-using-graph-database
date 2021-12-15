# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

logger = logging.getLogger(__name__)


class WrongFileException(Exception):
    def __init__(self, input_file_name: str, target_get_file_name: str):
        logger.debug(f"{input_file_name} != {target_get_file_name}")
        super().__init__()


def make_validate_file_name(target_file_name: str):
    def closure(input_file_name):
        if target_file_name not in input_file_name:
            logger.debug(f"{target_file_name} not in {input_file_name}")
            raise WrongFileException(input_file_name, target_file_name)

    return closure
