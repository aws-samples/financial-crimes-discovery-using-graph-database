// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


locals {
  cluster_identity = data.aws_eks_cluster.cluster.identity[0]
  oidc_string      = substr(local.cluster_identity.oidc[0].issuer, 8, -1)
}

resource "aws_iam_openid_connect_provider" "cluster_oidc_provider" {
  url = "https://accounts.google.com"

  client_id_list = [
    "266362248691-342342xasdasdasda-apps.googleusercontent.com",
  ]

  thumbprint_list = []
}

resource "aws_iam_role" "bastion_role" {
  name = "BastionRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}


resource "aws_iam_role" "neptune_role" {
  name = "NeptuneLoaderRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "rds.amazonaws.com"
        }
      },
    ]
  })
}


data "aws_iam_policy_document" "rdfox_assume_role_policy" {
  statement {
    sid     = "1"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${local.oidc_string}"]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_string}:sub"
      values   = ["system:serviceaccount:${local.rdfox_namespace}:${local.rdfox_service_account}"]
    }
  }
}

resource "aws_iam_role" "rdfox_pod_role" {
  assume_role_policy = data.aws_iam_policy_document.rdfox_assume_role_policy.json
  name               = "RDFox_Pod_Role"
}

resource "aws_iam_role" "lambda_scheduler_role" {
  name = "LambdaSchedulerRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role" "lambda_bulkloader_role" {
  name = "LambdaProcessInferenceRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role" "lambda_periodic_role" {
  name = "LambdaRefreshBulkLoadRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_iam_role" "backup_iam_role" {
  name               = "BackupRole"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["sts:AssumeRole"],
      "Effect": "allow",
      "Principal": {
        "Service": ["backup.amazonaws.com"]
      }
    }
  ]
}
POLICY
}