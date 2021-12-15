// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


variable "name" {
  type = string
}

variable "kms_key" {
  type = string
}

variable "global_secondary_index_name" {
  type = string
}

variable "global_secondary_index_pk" {
  type = string
}

variable "projection_attributes" {
  type = list(string)
}

