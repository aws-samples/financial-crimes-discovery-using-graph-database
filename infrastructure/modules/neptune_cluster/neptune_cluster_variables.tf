// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


variable "name" {
  type = string
}

variable "private_subnets" {
  type = list(string)
}

variable "iam_role" {
  type = string
}

variable "neptune_writer_instance_type" {
  type    = string
  default = "db.r5d.large"
}

variable "neptune_reader_instance_type" {
  type    = string
  default = "db.t3.medium"
}

variable "neptune_second_reader_instance_type" {
  type = string
  default = "db.t3.medium"
}

variable "security_group" {
  type = string
}

variable "query_timeout" {
  type = number
}

variable "deploy_rr" {
  type = bool
}

variable "deploy_second_rr" {
  type = bool
}


