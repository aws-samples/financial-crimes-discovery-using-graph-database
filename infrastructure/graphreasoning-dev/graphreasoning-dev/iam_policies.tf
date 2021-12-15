// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_iam_policy" "neptune_access_policy" {
  name        = "${var.name}-neptune-access-policy"
  description = "Policy to allow access to Neptune cluster and instances"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["arn:aws:neptune-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.id}:${module.neptune.cluster_resource_id}/*"],
      "Action": ["neptune-db:*"],
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "triple_store_read_write" {
  name        = "${var.name}-triple-read-write"
  description = "Policy to read and write from the triple store (input) bucket"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["${module.triple_store.bucket.arn}", "${module.triple_store.bucket.arn}/*"],
      "Action": ["s3:Get*", "s3:List*", "s3:Put*"],
      "Effect": "Allow"
    },
    {
      "Resource": ["${module.triple_store.bucket_key.arn}"],
      "Action": ["kms:Decrypt"],
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_policy" "rule_store_read" {
  name        = "${var.name}-rule-store-read"
  description = "Policy to read from the rule store bucket"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["${module.rule_store.bucket.arn}", "${module.rule_store.bucket.arn}/*"],
      "Action": ["s3:Get*", "s3:List*"],
      "Effect": "Allow"
    },
    {
      "Resource": ["${module.rule_store.bucket_key.arn}"],
      "Action": ["kms:Decrypt"],
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_policy" "output_store_read_write" {
  name        = "${var.name}-output-store-read_write"
  description = "Policy to read and write from the output store bucket"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["${module.output_store.bucket.arn}", "${module.output_store.bucket.arn}/*"],
      "Action": ["s3:Get*", "s3:List*", "s3:Put*"],
      "Effect": "Allow"
    },
    {
      "Resource": ["${module.output_store.bucket_key.arn}"],
      "Action": ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey"],
      "Effect": "Allow"
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "pass_loader" {
  statement {
    sid = "1"

    actions = [
      "iam:GetRole",
      "iam:PassRole"
    ]

    resources = [
      "${aws_iam_role.neptune_role.arn}",
    ]
  }
}

resource "aws_iam_policy" "pass_loader" {
  name   = "${var.name}-pass-loader-policy"
  path   = "/"
  policy = data.aws_iam_policy_document.pass_loader.json
}

resource "aws_iam_policy" "cc_policy" {
  name        = "${var.name}-cc-policy"
  description = "Access to CodeCommit"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["*"],
      "Action": ["codecommit:*"],
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "db_write_policy" {
  name        = "${var.name}-db-write-policy"
  description = "Policy to write to DynamoDB state table"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["${module.dynamodb.db_name.arn}", "${module.dynamodb.db_name.arn}/*"],
      "Action": ["dynamodb:*"],
      "Effect": "Allow"
    },
    {
      "Resource": ["${aws_kms_key.db_table.arn}"],
      "Action": ["kms:Decrypt"],
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_network_access" {
  name        = "${var.name}-lambda-network-policy"
  description = "Policy to allow Lambda to configure network interfaces in the VPC and access SSM Parameters"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": "*",
      "Action": ["ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DeleteNetworkInterface", "ssm:DescribeParameters", "ssm:GetParameters", "ssm:GetParametersByPath"],
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "eks_access" {
  name        = "${var.name}-lambda-eks-policy"
  description = "Policy to allow Lambda to access eks cluster"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Resource": ["${module.eks.cluster_arn}"],
      "Action": ["eks:DescribeCluster"],
      "Effect": "Allow"
    }
  ]
}
EOF
}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy" "aws_backup_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}


data "aws_iam_policy" "ssm_policy" {
  arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}


data "aws_iam_policy_document" "describe_rds" {
  statement {
    sid       = "1"
    effect    = "Allow"
    actions   = ["rds:Describe*"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "describe_rds" {
  policy = data.aws_iam_policy_document.describe_rds.json
  name   = "DescribeRDS"
}

data "aws_iam_policy_document" "publish_notification" {
  statement {
    sid       = "1"
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_cloudformation_stack.sns_topic.outputs["ARN"]]
  }
}

data "aws_iam_policy_document" "describe_instances" {
  statement {
    sid       = "1"
    effect    = "Allow"
    actions   = ["ec2:DescribeInstances"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "describe_instances" {
  policy = data.aws_iam_policy_document.describe_instances.json
  name   = "DescribeInstances"
}

resource "aws_iam_policy" "publish_notification" {
  policy = data.aws_iam_policy_document.publish_notification.json
  name   = "PublishNotification"
}

# Bastion role attachment policies
resource "aws_iam_role_policy_attachment" "bastion_attach_ssm" {
  role       = aws_iam_role.bastion_role.name
  policy_arn = data.aws_iam_policy.ssm_policy.arn
}

resource "aws_iam_role_policy_attachment" "bastion_attach_pass_loader" {
  role       = aws_iam_role.bastion_role.name
  policy_arn = aws_iam_policy.pass_loader.arn
}

resource "aws_iam_role_policy_attachment" "bastion_attach_triple_store" {
  role       = aws_iam_role.bastion_role.name
  policy_arn = aws_iam_policy.triple_store_read_write.arn
}

resource "aws_iam_role_policy_attachment" "bastion_attach_cc" {
  role       = aws_iam_role.bastion_role.name
  policy_arn = aws_iam_policy.cc_policy.arn
}

resource "aws_iam_role_policy_attachment" "bastion_attach_neptune" {
  role       = aws_iam_role.bastion_role.name
  policy_arn = aws_iam_policy.neptune_access_policy.arn
}

# Neptune role attachment policies

resource "aws_iam_role_policy_attachment" "neptune_attach_triple_store" {
  role       = aws_iam_role.neptune_role.name
  policy_arn = aws_iam_policy.triple_store_read_write.arn
}

resource "aws_iam_role_policy_attachment" "neptune_attach_output_store" {
  role       = aws_iam_role.neptune_role.name
  policy_arn = aws_iam_policy.output_store_read_write.arn
}

# Rdfox role attachment policies

resource "aws_iam_role_policy_attachment" "rdfox-triple-store" {
  role       = aws_iam_role.rdfox_pod_role.name
  policy_arn = aws_iam_policy.triple_store_read_write.arn
}

resource "aws_iam_role_policy_attachment" "rdfox-rule-store" {
  role       = aws_iam_role.rdfox_pod_role.name
  policy_arn = aws_iam_policy.rule_store_read.arn
}

resource "aws_iam_role_policy_attachment" "rdfox-output-store" {
  role       = aws_iam_role.rdfox_pod_role.name
  policy_arn = aws_iam_policy.output_store_read_write.arn
}


# Lambda Scheduler role attachment policies

resource "aws_iam_role_policy_attachment" "lambdascheduler-triple-store-r-attach" {
  role       = aws_iam_role.lambda_scheduler_role.name
  policy_arn = aws_iam_policy.triple_store_read_write.arn
}

resource "aws_iam_role_policy_attachment" "lambdascheduler-ddb-rw-attach" {
  role       = aws_iam_role.lambda_scheduler_role.name
  policy_arn = aws_iam_policy.db_write_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambdascheduler-execution" {
  role       = aws_iam_role.lambda_scheduler_role.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}

resource "aws_iam_role_policy_attachment" "lambdascheduler-vpc-access" {
  role       = aws_iam_role.lambda_scheduler_role.name
  policy_arn = aws_iam_policy.lambda_network_access.arn
}

resource "aws_iam_role_policy_attachment" "lambdascheduler-eks-access" {
  role       = aws_iam_role.lambda_scheduler_role.name
  policy_arn = aws_iam_policy.eks_access.arn
}


resource "aws_iam_role_policy_attachment" "lambdaschedule-describe-ec2" {
  role       = aws_iam_role.lambda_scheduler_role.name
  policy_arn = aws_iam_policy.describe_instances.arn
}


# Lambda Bulk Loader role attachment policies

resource "aws_iam_role_policy_attachment" "lambdabulkloader-output-store-rw-attach" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = aws_iam_policy.output_store_read_write.arn
}

resource "aws_iam_role_policy_attachment" "lambdabulkloader-neptune-rw-attach" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = aws_iam_policy.neptune_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambdabulkloader-ddb-rw-attach" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = aws_iam_policy.db_write_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambdabulkloader-execution" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}

resource "aws_iam_role_policy_attachment" "lambdabulkloader-vpc-access" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = aws_iam_policy.lambda_network_access.arn
}

resource "aws_iam_role_policy_attachment" "lambdabulkloader_attach_pass_loader" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = aws_iam_policy.pass_loader.arn
}

resource "aws_iam_role_policy_attachment" "lambdabulkloader_describe_rds" {
  role       = aws_iam_role.lambda_bulkloader_role.name
  policy_arn = aws_iam_policy.describe_rds.arn
}

# Lambda Periodic Scheduler role attachment policies

resource "aws_iam_role_policy_attachment" "lambdaperiodic-neptune-rw-attach" {
  role       = aws_iam_role.lambda_periodic_role.name
  policy_arn = aws_iam_policy.neptune_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambdaperiodic-ddb-rw-attach" {
  role       = aws_iam_role.lambda_periodic_role.name
  policy_arn = aws_iam_policy.db_write_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambdaperiodic-execution" {
  role       = aws_iam_role.lambda_periodic_role.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}

resource "aws_iam_role_policy_attachment" "lambdaperiodic-vpc-access" {
  role       = aws_iam_role.lambda_periodic_role.name
  policy_arn = aws_iam_policy.lambda_network_access.arn
}

resource "aws_iam_role_policy_attachment" "lambdaperiodic_attach_pass_loader" {
  role       = aws_iam_role.lambda_periodic_role.name
  policy_arn = aws_iam_policy.pass_loader.arn
}

resource "aws_iam_role_policy_attachment" "lambdaperiodic-sns-publish" {
  role       = aws_iam_role.lambda_periodic_role.name
  policy_arn = aws_iam_policy.publish_notification.arn
}

# AWS Backup Role

resource "aws_iam_role_policy_attachment" "backup_role_to_policy" {
  role       = aws_iam_role.backup_iam_role.name
  policy_arn = data.aws_iam_policy.aws_backup_policy.arn
}
