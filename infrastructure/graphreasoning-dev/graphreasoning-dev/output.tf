// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


output "cluster_name" {
  value = module.eks.cluster_id
}

output "neptune_endpoint" {
  value = module.neptune.primary_endpoint
}

output "bastion_public_hostname" {
  value = var.create_dev_instance ? module.bastion_instance[0].bastion_public_hostname : null
}

output "triple_store" {
  value = module.triple_store.bucket.id
}

output "rule_store" {
  value = module.rule_store.bucket.id
}

output "output_store" {
  value = module.output_store.bucket.id
}

output "neptune_loader_role" {
  value = aws_iam_role.neptune_role.arn
}

output "workers_asg_names" {
  value = module.eks.workers_asg_names
}

output "topic_arn" {
  value       = "${aws_cloudformation_stack.sns_topic.outputs["ARN"]}"
  description = "Email SNS topic ARN"
}

output "file_bucket"{
  value = module.code_bucket.bucket.id
}