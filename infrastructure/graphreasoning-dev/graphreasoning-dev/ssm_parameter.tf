// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_ssm_parameter" "db_name" {
  name  = "/parameter/pipeline_control/JOB_TABLE_NAME"
  type  = "String"
  value = module.dynamodb.db_name.id
}

resource "aws_ssm_parameter" "neptune_cluster_endpoint" {
  name  = "/parameter/pipeline_control/NEPTUNE_CLUSTER_ENDPOINT"
  type  = "String"
  value = "${module.neptune.primary_endpoint}:8182"
}

resource "aws_ssm_parameter" "eks_cluster_name" {
  name  = "/parameter/pipeline_control/CLUSTER_NAME"
  type  = "String"
  value = module.eks.cluster_id
}

resource "aws_ssm_parameter" "log_level" {
  name  = "/parameter/pipeline_control/LOG_LEVEL"
  type  = "String"
  value = "debug"
}

resource "aws_ssm_parameter" "db_index_name" {
  name  = "/parameter/pipeline_control/INDEX_NAME"
  type  = "String"
  value = module.dynamodb.index_name
}

resource "aws_ssm_parameter" "bulkloader_sns_topic" {
  name  = "/parameter/pipeline_control/BULKLOAD_TOPIC"
  type  = "String"
  value = "${aws_cloudformation_stack.sns_topic.outputs["ARN"]}"
}

resource "aws_ssm_parameter" "neptune_iam-role_arn" {
  name  = "/parameter/pipeline_control/NEPTUNE_IAM_ROLE_ARN"
  type  = "String"
  value = aws_iam_role.neptune_role.arn
}