// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_dynamodb_table" "db_state_table" {
  name           = var.name
  billing_mode   = "PAY_PER_REQUEST"
  server_side_encryption {
      enabled = true
      kms_key_arn = var.kms_key
  }
  hash_key       = "pk"
  range_key      = "sk"
  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }
  attribute {
    name = var.global_secondary_index_pk
    type = "S"
  }
  global_secondary_index {
    name               = var.global_secondary_index_name
    hash_key           = var.global_secondary_index_pk
    projection_type    = "INCLUDE"
    non_key_attributes = var.projection_attributes
  }
}

output "db_name" {
  value = aws_dynamodb_table.db_state_table
}

output "index_name" {
  value = var.global_secondary_index_name
}