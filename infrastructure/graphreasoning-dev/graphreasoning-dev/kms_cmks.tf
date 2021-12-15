// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_kms_key" "worker_ebs" {
  description             = "Key for EKS worker node disk volumes"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.asg_kms.json 
}

resource "aws_kms_key" "db_table" {
  description             = "Key for DynamoDB state table"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_key" "ecr_pre_rdfox" {
  description             = "Key for ECR repo pre-rdfox"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_key" "ecr_post_rdfox" {
  description             = "Key for ECR repo post-rdfox"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_key" "ecr_custom_rdfox" {
  description             = "Key for ECR repo custom-rdfox"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_key" "backup_vault" {
  description             = "Key for AWS Backup Vault"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

data "aws_iam_policy_document" "asg_kms" {

  statement {
    sid = "1"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = [
      "kms:*",
    ]

    resources = [
      "*"
    ]
  }

  statement {
    sid = "2"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"]
    }

    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    sid = "3"

    actions = [
      "kms:CreateGrant",
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"]
    }

    resources = [
      "*"
    ]
  }
}
