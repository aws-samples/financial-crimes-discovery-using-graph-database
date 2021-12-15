# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import sys

import environ
from ssm_parameter_store import EC2ParameterStore

from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneMode,
    NeptuneParallelism,
)


def str_to_log_level(input):
    log_level = getattr(logging, input.upper(), logging.INFO)
    print(f"Log level {input} {input.upper()} = {log_level}")
    return log_level


if not "pytest" in sys.modules:
    parameter_store = EC2ParameterStore()
    pipeline_control_parameters = parameter_store.get_parameters_by_path(
        "/parameter/pipeline_control/", strip_path=True
    )
    EC2ParameterStore.set_env(pipeline_control_parameters)
    print(pipeline_control_parameters)


@environ.config(prefix="")
class AppConfig:
    cluster_name = environ.var(default="eks_cluster2")
    job_table_name = environ.var(default="Jobs_Test")
    jobspec_name = environ.var(default="rdfoxjob.json")
    rdfoxlog_name = environ.var(default="rdfox.log")
    neptune_cluster_endpoint = environ.var(
        default="neptune.cluster-abcdefghijklmn.ap-southeast-1.neptune.amazonaws.com:8182"
    )
    aws_default_region = environ.var(default="ap-southeast-1")
    job_id_delimeter = environ.var(default="_")
    bulkload_topic = environ.var(default="something")
    neptune_iam_role_arn = environ.var(
        default="arn:aws:iam::1234567891011:role/NeptuneLoaderRole"
    )
    neptune_source_format = "turtle"
    neptune_update_single_cardinality_properties = True
    neptune_parallelism = NeptuneParallelism.OVERSUBSCRIBE
    neptune_queue_request = True
    neptune_mode = NeptuneMode.AUTO
    neptune_fail_on_error = False
    log_level = environ.var(default="info", converter=str_to_log_level)


# Doing this so I can get my env logged first
_t_app_configuration = environ.to_config(AppConfig)

logger = logging.getLogger("pipeline_control")
logger.setLevel(_t_app_configuration.log_level)
if not logger.hasHandlers():
    c_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

logger.debug(_t_app_configuration)

app_configuration = _t_app_configuration
