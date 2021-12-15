# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from .global_fixtures.gfixtures_infrastructure import *
from .global_fixtures.gfixtures_job_configurations import *
from .global_fixtures.gfixtures_post_inference import *
from .global_fixtures.gfixtures_rdfox_job import *
from .global_fixtures.gfixtures_side_effect_patches import *
from .test_variables import *

logger = logging.getLogger("tests")
logger.setLevel(logging.INFO)

log = logging.getLogger("pynamodb")
log.setLevel(logging.INFO)

log2 = logging.getLogger("botocore")
log2.setLevel(logging.INFO)
