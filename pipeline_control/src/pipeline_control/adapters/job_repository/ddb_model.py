# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datetime

from pynamodb.attributes import (
    JSONAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

import app_config


class JobStatusIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index
    """

    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "Job_Status_Index"
        # All attributes are projected
        projection = AllProjection()
        read_capacity_units = 2
        write_capacity_units = 1

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    job_status = UnicodeAttribute(hash_key=True)


class DDBJob(Model):
    class Meta:
        table_name = app_config.app_configuration.job_table_name
        region = app_config.app_configuration.aws_default_region

    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)
    job_configuration = JSONAttribute(default={})
    time_to_load_neptune = NumberAttribute(default=0)
    job_status = UnicodeAttribute(default="CREATED")
    job_created = UTCDateTimeAttribute(default=datetime.datetime.now())
    job_updated = UTCDateTimeAttribute(default=datetime.datetime.now())
    kubernetes_name = UnicodeAttribute(default="N/A")
    kubernetes_worker_type = UnicodeAttribute(default="N/A")
    neptune_load_id = UnicodeAttribute(default="N/A")
    neptune_statistics_raw = JSONAttribute(default={})
    neptune_statistics = JSONAttribute(default={})
    rdfox_statistics = JSONAttribute(default={})
    rdfox_statistics_raw = UnicodeAttribute(default="")
    job_id = UnicodeAttribute(default="")
    key = UnicodeAttribute(default="")
    job_status_index = JobStatusIndex()
    neptune_writer_instance = UnicodeAttribute(default="")
