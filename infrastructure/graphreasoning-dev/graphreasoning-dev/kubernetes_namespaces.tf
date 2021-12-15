// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "kubernetes_namespace" "rdfox_namespace" {
  metadata {
    annotations = {
      name = var.rdfox_namespace
    }

    name = var.rdfox_namespace
  }
}
