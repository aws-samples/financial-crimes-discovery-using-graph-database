// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_lambda_function" "lambda_periodic_scheduler" {
  source_code_hash = var.source_code_hash
  s3_bucket        = var.code_s3_bucket
  s3_key           = var.code_s3_file
  function_name    = "refresh_bulkload"
  role             = var.iam_role
  handler          = "lambda_entry_points.handle_refresh_bulkload"
  runtime          = "python3.7"
  timeout          = 60
  memory_size      = 512
  vpc_config {
    security_group_ids = [var.sg_ids]
    subnet_ids         = var.subnet_ids
  }
  environment {
    variables = {
      SSM_PREFIX = var.ssm_prefix
    }
  }
}

resource "aws_cloudwatch_event_rule" "periodic_scheduler_trigger" {
  name                = "periodic_scheduler_trigger"
  description         = "Triggers Periodic Scheduler Lambda function every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "periodic_scheduler_trigger_event" {
  rule      = aws_cloudwatch_event_rule.periodic_scheduler_trigger.name
  target_id = "read_neptune_db"
  arn       = aws_lambda_function.lambda_periodic_scheduler.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.lambda_periodic_scheduler.arn
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.periodic_scheduler_trigger.arn
  source_account = var.account_id
}





