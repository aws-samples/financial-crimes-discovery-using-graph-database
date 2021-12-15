// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_lambda_function" "lambda_bulk_loader" {
  source_code_hash = var.source_code_hash
  s3_bucket        = var.code_s3_bucket
  s3_key           = var.code_s3_file
  function_name    = "process_inference"
  role             = var.iam_role
  handler          = "lambda_entry_points.handle_process_inference"
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

resource "aws_lambda_permission" "allow_bucket" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.lambda_bulk_loader.arn
  principal      = "s3.amazonaws.com"
  source_arn     = var.s3bucket_arn
  source_account = var.account_id
}

resource "aws_s3_bucket_notification" "ouput_store_notification" {
  bucket = var.s3bucket
  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda_bulk_loader.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".log"
  }
  depends_on = [aws_lambda_permission.allow_bucket]
}


