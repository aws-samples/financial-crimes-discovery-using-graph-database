// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


variable "iam_role" {
  type = string
}

variable "account_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "sg_ids" {
  type = string
}

variable "ssm_prefix" {
  type = string
}

variable "code_s3_bucket" {
  type = string
}

variable "code_s3_file" {
  type = string
}

variable "email" {
  type = string
}
variable "source_code_hash" {
  type = string
}

