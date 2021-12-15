// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "kubernetes_service_account" "rdfox_service_account" {
  metadata {
    name      = "rdfox-service-account"
    namespace = local.rdfox_namespace

    annotations = {
      "eks.amazonaws.com/role-arn" = "${aws_iam_role.rdfox_pod_role.arn}"
    }
  }
}
