// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_neptune_subnet_group" "default" {
  name       = "main"
  subnet_ids = var.private_subnets

  tags = {
    Name = "${var.name}-subnet-group"
  }
}

resource "aws_neptune_cluster_parameter_group" "graphreasoning" {
  family      = "neptune1"
  name        = "example"
  description = "neptune cluster parameter group"


  parameter {
    name  = "neptune_enable_audit_log"
    value = 1
  }
  parameter {
    name  = "neptune_query_timeout"
    value = var.query_timeout
  }
}

resource "aws_neptune_cluster" "default" {
  cluster_identifier                   = "neptune"
  engine                               = "neptune"
  backup_retention_period              = 5
  preferred_backup_window              = "07:00-09:00"
  skip_final_snapshot                  = true
  iam_database_authentication_enabled  = true
  apply_immediately                    = true
  iam_roles                            = [var.iam_role]
  storage_encrypted                    = true
  neptune_subnet_group_name            = aws_neptune_subnet_group.default.name
  vpc_security_group_ids               = [var.security_group]
  neptune_cluster_parameter_group_name = aws_neptune_cluster_parameter_group.graphreasoning.name


}

resource "aws_neptune_cluster_instance" "primary" {
  count              = 1
  cluster_identifier = aws_neptune_cluster.default.id
  engine             = "neptune"
  instance_class     = var.neptune_writer_instance_type
  apply_immediately  = true
  promotion_tier     = 0
}

resource "aws_neptune_cluster_instance" "rr" {
  count              = var.deploy_rr ? 1 : 0
  cluster_identifier = aws_neptune_cluster.default.id
  engine             = "neptune"
  instance_class     = var.neptune_reader_instance_type
  apply_immediately  = true
  promotion_tier     = 1
}

resource "aws_neptune_cluster_instance" "secondary_rr" {
  count              = var.deploy_second_rr ? 1 : 0
  cluster_identifier = aws_neptune_cluster.default.id
  engine             = "neptune"
  instance_class     = var.neptune_second_reader_instance_type
  apply_immediately  = true
  promotion_tier     = 1
}


output "primary_endpoint" {
  value = aws_neptune_cluster.default.endpoint
}

output "cluster_arn" {
  value = aws_neptune_cluster.default.arn
}

output "cluster_resource_id" {
  value = aws_neptune_cluster.default.cluster_resource_id
}

output "primary_instance_resource_id" {
  value = aws_neptune_cluster_instance.primary[0].dbi_resource_id
}

output "rr_instance_resource_id" {
  value = var.deploy_rr ? aws_neptune_cluster_instance.rr[0].dbi_resource_id : null 
}

output "second_rr_instance_resource_id" {
  value = var.deploy_second_rr ? aws_neptune_cluster_instance.secondary_rr[0].dbi_resource_id : null 
}
