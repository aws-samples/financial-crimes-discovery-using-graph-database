// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  oidc_string = substr(var.cluster_identifier, 8, -1)
}

data "aws_iam_policy_document" "eks_elb_assume_role_policy" {
  statement {
    sid     = "1"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${local.oidc_string}"]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_string}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }
  }
}

resource "aws_iam_role" "eks_elb_role" {
  assume_role_policy = data.aws_iam_policy_document.eks_elb_assume_role_policy.json
  name               = "AmazonEKSLoadBalancerControllerRole"
}

resource "kubernetes_service_account" "elb_controller" {
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = "kube-system"
    labels = {
      "app.kubernetes.io/component" = "controller"
      "app.kubernetes.io/name"      = "aws-load-balancer-controller"
    }
    annotations = {
      "eks.amazonaws.com/role-arn" = "${aws_iam_role.eks_elb_role.arn}"
    }
  }
}

resource "helm_release" "aws_eks_elb_controller" {
  name = "aws-load-balancer-controller"

  chart      = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  namespace  = "kube-system"

  set {
    name  = "replicaCount"
    value = 1
  }

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "serviceAccount.create"
    value = false
  }
  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }
}

resource "aws_iam_role_policy_attachment" "eks-efs-attach" {
  role       = aws_iam_role.eks_elb_role.name
  policy_arn = aws_iam_policy.eks_elb_policy.arn
}

