// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


locals {
  trusted_cidrs        = [var.dev_security_allowed_ingress, var.cidr_block]
  trusted_prefix_lists = var.trusted_prefixlists
}

resource "aws_security_group" "dev_security_group" {
  description = "Allow SSH from nominated dev machine"
  vpc_id      = module.vpc.vpc_id
  ingress {
    description     = "TLS from nominated host"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  ingress {
    description     = "TLS from nominated host"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  ingress {
    description = "HTTP from nominated host"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = local.trusted_cidrs
  }
  ingress {
    description     = "RDFox from nominated host"
    from_port       = local.rdfox_port
    to_port         = local.rdfox_port
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_security_group" "rdfox_security_group" {
  description = "Allow access to RDFox from Dev and VPC"
  vpc_id      = module.vpc.vpc_id
  ingress {
    description     = "TLS from dev host and VPC"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  ingress {
    description     = "HTTP from dev host and VPC"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  ingress {
    description     = "HTTP from dev host and VPC"
    from_port       = local.rdfox_port
    to_port         = local.rdfox_port
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_security_group" "rdf_store_mtsecurity_group" {
  name        = "rdf_store_sg"
  description = "Allow access to RDF EFS mount"
  vpc_id      = module.vpc.vpc_id
  ingress {
    description     = "TLS from RDFox container"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

}


resource "aws_security_group" "neptune_security_group" {
  name        = "neptune_sg"
  description = "Allow access to Neptune from Dev and EKS"
  vpc_id      = module.vpc.vpc_id
  ingress {
    description     = "Neptune port from nominated host"
    from_port       = var.neptune_port
    to_port         = var.neptune_port
    protocol        = "tcp"
    cidr_blocks     = local.trusted_cidrs
    prefix_list_ids = local.trusted_prefix_lists
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_security_group" "lambda_sg" {
  name        = "lambda_securitygroup"
  description = "Allow Lambda outbound access"
  vpc_id      = module.vpc.vpc_id
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}


resource "aws_security_group" "eks_workers" {
  name        = "EKS workers to ECR"
  description = "Allow Lambda outbound access"
  vpc_id      = module.vpc.vpc_id
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_security_group" "vpc_endpoints2" {
  name        = "vpc endpoints2"
  description = "Allow access to AWS APIs"
  vpc_id      = module.vpc.vpc_id
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "TCP"
    security_groups = [aws_security_group.lambda_sg.id, aws_security_group.neptune_security_group.id, aws_security_group.dev_security_group.id, aws_security_group.dev_security_group.id, aws_security_group.eks_workers.id]
  }
}
