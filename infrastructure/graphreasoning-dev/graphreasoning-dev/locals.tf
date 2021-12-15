// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


locals {
  rdfox_service_account = "rdfox-service-account"
  eks_subnet_tags = {
    "kubernetes.io/cluster/${module.eks.cluster_id}" = "shared"
    "kubernetes.io/role/elb"                         = "1"
  }
  region          = var.target_region
  private_subnets = ["${var.priv_1}", "${var.priv_2}", "${var.priv_3}"]
  public_subnets  = ["${var.pub_1}", "${var.pub_2}", "${var.pub_3}"]
  rdfox_port      = 12110
  rdfox_namespace = kubernetes_namespace.rdfox_namespace.metadata[0].name
}
