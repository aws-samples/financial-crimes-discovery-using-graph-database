// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

variable "target_account" {
  type = string
}

variable "target_region" {
  type = string
}

variable "deployment_role" {
  type = string
}

variable "account_alias" {
  type = string
}

module "bootstrap" {
  source = "trussworks/bootstrap/aws"

  region        = var.target_region
  account_alias = var.account_alias
}
