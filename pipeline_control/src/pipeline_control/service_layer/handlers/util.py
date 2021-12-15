# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import boto3

from app_config import app_configuration
from pipeline_control.adapters.neptune_loader.neptune_loader_configuration import (
    NeptuneBulkloaderConfiguration,
)

logger = logging.getLogger(__name__)


def neptune_config_from_app_config():
    neptune_config_dict = {
        "cluster_endpoint": app_configuration.neptune_cluster_endpoint,
        "iam_role": app_configuration.neptune_iam_role_arn,
        "source_format": app_configuration.neptune_source_format,
        "update_single_cardinality_properties": app_configuration.neptune_update_single_cardinality_properties,
        "parallelism": app_configuration.neptune_parallelism,
        "queue_request": app_configuration.neptune_queue_request,
        "source": "",
        "region": app_configuration.aws_default_region,
        "mode": app_configuration.neptune_mode,
        "fail_on_error": app_configuration.neptune_fail_on_error,
    }
    return NeptuneBulkloaderConfiguration(**neptune_config_dict)


def neptune_instance_type_from_endpoint(cluster_endpoint: str):
    primary_instance = neptune_primary_instance_from_endpoint(cluster_endpoint)
    instance_type = neptune_instance_type_from_identifier(primary_instance)
    return instance_type


def ec2_instance_from_name(instance_name: str):
    ec2 = boto3.resource("ec2")
    the_instance = list(
        ec2.instances.filter(
            Filters=[{"Name": "private-dns-name", "Values": [instance_name]}]
        )
    )
    if len(the_instance) == 1:
        return the_instance[0]
    return None


def ec2_instance_type_from_name(instance_name: str):
    the_instance = ec2_instance_from_name(instance_name)
    return the_instance.instance_type


def neptune_primary_instance_from_endpoint(writer_endpoint: str):
    neptune = boto3.client("neptune")
    cluster_identifier = writer_endpoint.split(".")[0]
    primary_instance = None
    try:
        cluster_response = neptune.describe_db_clusters(
            DBClusterIdentifier=cluster_identifier
        )
        # https://docs.aws.amazon.com/neptune/latest/userguide/api-clusters.html#DBCluster
        cluster_members = cluster_response["DBClusters"][0]["DBClusterMembers"]
        cluster_writer = None
        for cluster_member in cluster_members:
            if cluster_member["IsClusterWriter"] is True:
                cluster_writer = cluster_member
                break
        primary_instance = cluster_writer["DBInstanceIdentifier"]
    except Exception:
        logger.warn("No writer instance found for {writer_endpoint}")
        raise
    return primary_instance


def neptune_instance_type_from_identifier(instance_identifier: str):
    neptune = boto3.client("neptune")
    instance_type = "unknown"
    try:
        instance_response = neptune.describe_db_instances(
            DBInstanceIdentifier=instance_identifier
        )
        instance_type = instance_response["DBInstances"][0]["DBInstanceClass"]
    except Exception:
        logger.warn("No instance type found for {instance_identifier}")
    return instance_type
