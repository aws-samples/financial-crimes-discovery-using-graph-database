// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


provider "aws" {
  # Update desired region
  region                  = var.target_region
  shared_credentials_file = "~/.aws/config"
  # Update account IDs
  allowed_account_ids = ["${var.target_account}"]

  assume_role {
    # Fill in the session and role you want to use here
    role_arn     = "arn:aws:iam::${var.target_account}:role/${var.deployment_role}"
    session_name = "mysessionfordeploy"
  }
}
