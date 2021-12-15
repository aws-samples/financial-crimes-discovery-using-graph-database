// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


module "vpc" {
  source               = "github.com/terraform-aws-modules/terraform-aws-vpc"
  cidr                 = var.cidr_block
  azs                  = ["${local.region}a", "${local.region}b", "${local.region}c"]
  public_subnets       = local.public_subnets
  private_subnets      = local.private_subnets
  enable_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = merge(local.eks_subnet_tags, {
    Name = "${var.name}-public"
  })

  private_subnet_tags = {
    Name = "${var.name}-private"
  }

  vpc_tags = {
    Name = "${var.name}"
  }
}
