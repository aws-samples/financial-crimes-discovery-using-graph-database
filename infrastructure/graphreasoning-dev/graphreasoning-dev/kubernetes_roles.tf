// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "kubernetes_role" "ns_role" {
  metadata {
    name = "rdfox-role"
    namespace = var.rdfox_namespace
  }
  rule {
    api_groups     = ["batch", ""]
    resources      = ["jobs", "pods"]
    verbs          = ["get", "list", "watch", "create", "update"]
  }
}

resource "kubernetes_role_binding" "rdfox_role_binding" {
  metadata {
    name = "${var.rdfox_namespace}-rolebinding"
    namespace = var.rdfox_namespace
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = "rdfox-role"
  }
  subject {
    kind      = "Group"
    name      = "${var.rdfox_namespace}-group"
    api_group = "rbac.authorization.k8s.io"
  }
}
