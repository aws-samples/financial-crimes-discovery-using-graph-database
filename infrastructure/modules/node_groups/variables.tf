// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

variable "cluster_name" {
  description = "Name of parent cluster"
  type        = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "name" {
  type = string
}

variable "desired" {
  type    = number
  default = 3
}

variable "min" {
  type    = number
  default = 1
}

variable "max" {
  type    = number
  default = 3
}
