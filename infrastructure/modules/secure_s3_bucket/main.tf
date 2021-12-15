// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_kms_key" "bucket_key" {
  description = "Bucket SSE key"
}

resource "aws_s3_bucket" "the_bucket" {
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.bucket_key.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

output "bucket_key" {
  value = aws_kms_key.bucket_key
}


output "bucket" {
  value = aws_s3_bucket.the_bucket
}
