// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


variable "vpc" {
  type = string
}

variable "subnet" {
  type = string
}

variable "role" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "public_key" {
  type = string
}

variable "security_group" {
  type = string
}
