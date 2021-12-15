// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_key_pair" "dev_key" {
  key_name   = "dev-key"
  public_key = var.dev_public_key
  count      = var.create_dev_instance ? 1 : 0
}

module "bastion_instance" {
  source         = "../../modules/bastion_instance"
  count          = var.create_dev_instance ? 1 : 0
  vpc            = module.vpc.vpc_id
  subnet         = module.vpc.public_subnets[0]
  instance_type  = var.dev_instance_type
  public_key     = aws_key_pair.dev_key[0].id
  role           = aws_iam_role.bastion_role.name
  security_group = aws_security_group.dev_security_group.id
}

module "triple_store" {
  source = "../../modules/secure_s3_bucket"
}

module "rule_store" {
  source = "../../modules/secure_s3_bucket"
}

module "output_store" {
  source = "../../modules/secure_s3_bucket"
}

module "neptune" {
  name                                = "${var.name}_neptune_cluser"
  source                              = "../../modules/neptune_cluster"
  private_subnets                     = module.vpc.private_subnets
  iam_role                            = aws_iam_role.neptune_role.arn
  neptune_second_reader_instance_type = var.neptune_second_reader_instance_type
  neptune_reader_instance_type        = var.neptune_reader_instance_type
  neptune_writer_instance_type        = var.neptune_writer_instance_type
  security_group                      = aws_security_group.neptune_security_group.id
  query_timeout                       = var.neptune_querytimeout
  deploy_rr                           = var.deploy_rr
  deploy_second_rr                    = var.deploy_second_rr
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "${var.name}_eks_cluster2"
  cluster_version = "1.19"
  subnets         = module.vpc.private_subnets
  vpc_id          = module.vpc.vpc_id
  enable_irsa     = true
  map_roles = [{
    rolearn  = aws_iam_role.bastion_role.arn
    username = "admin"
    groups   = ["system:masters"]
    },
    {
      rolearn  = "arn:aws:iam::${var.target_account}:role/${var.deployment_role}"
      username = "admin"
      groups   = ["system:masters"]
    },
    {
      rolearn  = aws_iam_role.lambda_scheduler_role.arn
      username = "lambda-scheduler"
      groups   = ["${var.rdfox_namespace}-group"]
  }]

  worker_additional_security_group_ids = ["${aws_security_group.rdfox_security_group.id}", "${aws_security_group.eks_workers.id}"]

  worker_groups_launch_template = [
    {
      instance_type          = var.worker_node_instance_type
      desired_capacity       = var.worker_node_desired_capacity
      asg_min_size           = var.worker_node_min_capacity
      asg_desired_capacity   = var.worker_node_desired_capacity
      root_volume_size       = 3000
      root_volume_type       = "gp3"
      root_volume_throughput = 1000
      root_iops              = 4000
      root_kms_key_id        = aws_kms_key.worker_ebs.arn
      root_encrypted         = true

    },
    {
      instance_type          = var.secondary_worker_node_instance_type
      desired_capacity       = var.secondary_worker_node_desired_capacity
      asg_min_size           = var.secondary_worker_node_min_capacity
      asg_desired_capacity   = var.secondary_worker_node_desired_capacity
      root_volume_size       = 3000
      root_volume_type       = "gp3"
      root_volume_throughput = 1000
      root_iops              = 4000
      root_kms_key_id        = aws_kms_key.worker_ebs.arn
      root_encrypted         = true
    }
  ]
}

module "cluster_autoscaler" {
  source                           = "git::https://github.com/DNXLabs/terraform-aws-eks-cluster-autoscaler.git"
  enabled                          = true
  cluster_name                     = module.eks.cluster_id
  cluster_identity_oidc_issuer     = module.eks.cluster_oidc_issuer_url
  cluster_identity_oidc_issuer_arn = module.eks.oidc_provider_arn
  aws_region                       = data.aws_region.current.name
}

module "elb_controller" {
  source             = "../../modules/aws-load-balancer-controller"
  cluster_identifier = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
  cluster_name       = data.aws_eks_cluster.cluster.name
}


module "rdfox" {
  source                      = "../../modules/rdfox"
  license_path                = var.license_path
  password                    = var.password
  namespace                   = local.rdfox_namespace
  security_group              = aws_security_group.rdfox_security_group.id
  rdfox_port                  = local.rdfox_port
  rdfox_access_security_group = aws_security_group.dev_security_group.id
  depends_on                  = [module.elb_controller, module.eks]
  rdfox_service_account       = local.rdfox_service_account
  persistent_replicas         = var.rdfox_persistent_replicas
  acm_cert                    = var.acm_cert
}


module "code_bucket" {
  source = "../../modules/secure_s3_bucket"
}

resource "aws_s3_bucket_object" "file_input" {
  bucket = module.code_bucket.bucket.id
  key    = var.code_s3_file
  source = "../../../pipeline_control/dist/pipeline_control.zip"
}

locals {
  source_code_hash = filebase64sha256("../../../pipeline_control/dist/pipeline_control.zip")
}

module "lambda_scheduler" {
  source           = "../../modules/lambda_scheduler"
  source_code_hash = local.source_code_hash
  code_s3_bucket   = module.code_bucket.bucket.id
  code_s3_file     = aws_s3_bucket_object.file_input.id
  iam_role         = aws_iam_role.lambda_scheduler_role.arn
  subnet_ids       = module.vpc.private_subnets
  sg_ids           = aws_security_group.lambda_sg.id
  s3bucket_arn     = module.triple_store.bucket.arn
  s3bucket         = module.triple_store.bucket.id
  account_id       = data.aws_caller_identity.current.account_id
  ssm_prefix       = var.ssm_prefix
}

module "lambda_bulk_loader" {
  source           = "../../modules/lambda_bulk_loader"
  source_code_hash = local.source_code_hash
  code_s3_bucket   = module.code_bucket.bucket.id
  code_s3_file     = aws_s3_bucket_object.file_input.id
  iam_role         = aws_iam_role.lambda_bulkloader_role.arn
  subnet_ids       = module.vpc.private_subnets
  sg_ids           = aws_security_group.lambda_sg.id
  s3bucket_arn     = module.output_store.bucket.arn
  s3bucket         = module.output_store.bucket.id
  account_id       = data.aws_caller_identity.current.account_id
  ssm_prefix       = var.ssm_prefix
}

module "lambda_periodic_scheduler" {
  source           = "../../modules/lambda_periodic_scheduler"
  source_code_hash = local.source_code_hash
  code_s3_bucket   = module.code_bucket.bucket.id
  code_s3_file     = aws_s3_bucket_object.file_input.id
  iam_role         = aws_iam_role.lambda_periodic_role.arn
  subnet_ids       = module.vpc.private_subnets
  sg_ids           = aws_security_group.lambda_sg.id
  account_id       = data.aws_caller_identity.current.account_id
  ssm_prefix       = var.ssm_prefix
  email            = var.email
}

module "dynamodb" {
  source                      = "../../modules/dynamodb"
  name                        = var.db_name
  kms_key                     = aws_kms_key.db_table.arn
  global_secondary_index_name = var.global_secondary_index_name
  global_secondary_index_pk   = var.global_secondary_index_pk
  projection_attributes       = var.projection_attributes
}

data "template_file" "cloudformation_sns_stack" {
  template = file("sns-stack.json.tpl")
  vars = {
    display_name  = "${var.display_name}"
    subscriptions = "${join(",", formatlist("{ \"Endpoint\": \"%s\", \"Protocol\": \"%s\"  }", var.email, var.protocol))}"
  }
}
resource "aws_cloudformation_stack" "sns_topic" {
  name          = var.stack_name
  template_body = data.template_file.cloudformation_sns_stack.rendered
  tags = (merge(
    tomap({ "Name" = "${var.stack_name}" })
  ))
}

