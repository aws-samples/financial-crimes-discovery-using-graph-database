// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


variable "min" {
  type = number
}

variable "max" {
  type = number
}

variable "desired" {
  type = number
}

variable "name" {
  type = string
}

variable "target_account" {
  type = string
}

variable "target_region" {
  type = string
}

variable "deployment_role" {
  type = string
}

variable "cidr_block" {
  type = string
}

variable "pub_1" {
  type = string
}

variable "pub_2" {
  type = string
}

variable "pub_3" {
  type = string
}

variable "priv_1" {
  type = string
}

variable "priv_2" {
  type = string
}

variable "priv_3" {
  type = string
}

variable "neptune_writer_instance_type" {
  type    = string
  default = "db.r5d.large"
}

variable "neptune_reader_instance_type" {
  type    = string
  default = "db.t3.medium"
}

variable "neptune_second_reader_instance_type" {
  type = string
  default = "db.t3.medium"
}

variable "deploy_rr" {
  type    = bool
  default = true
}

variable "deploy_second_rr" {
  type    = bool
  default = true
}

variable "create_dev_instance" {
  type    = bool
  default = false
}

variable "dev_instance_type" {
  type    = string
  default = "m5.large"
}

variable "dev_security_allowed_ingress" {
  type    = string
  default = "192.168.1.1/32"
}

variable "trusted_prefixlists" {
  type    = list(string)
}

variable "neptune_port" {
  type    = string
  default = "8182"
}

variable "dev_public_key" {
  type    = string
  default = ""
}

variable "rdfox_namespace" {
  type    = string
  default = "ns-rdfox"
}

variable "worker_node_instance_type" {
  # Smallest recommended, where ~1.1Gb of 2Gb memory is available for the Kubernetes pods after ‘warming up’ Docker, Kubelet, and OS
  default = "r5.large"
  type    = string
}

variable "worker_node_min_capacity" {
  default = 0
  type    = number
}

variable "worker_node_desired_capacity" {
  default = 1
  type    = number
}

variable "secondary_worker_node_instance_type" {
  default = "r5.large"
  type    = string
}

variable "secondary_worker_node_min_capacity" {
  default = 0
  type    = number
}

variable "secondary_worker_node_desired_capacity" {
  default = 1
  type    = number
}

variable "neptune_public" {
  default = false
}

variable "db_name" {
  default = "DB-State-Table"
  type    = string
}

variable "global_secondary_index_name" {
  default = "Job_Status_Index"
  type    = string
}

variable "global_secondary_index_pk" {
  default = "job_status"
  type    = string
}

variable "projection_attributes" {
  default = ["job_id", "neptune_loader_id", "job_status"]
  type    = list(string)
}

variable "ssm_prefix" {
  default = "/parameter/pipeline_control/"
  type    = string
}

variable "code_s3_file" {
  default = "pipeline_control.zip"
  type    = string
}

variable "rdfox_persistent_replicas" {
  type    = number
  default = 0
}

variable "neptune_querytimeout" {
  type    = number
  default = 2147483647
}

variable "email" {
  type    = string
}

variable "stack_name" {
  default = "SNSStack"
  type    = string
}

variable "display_name" {
  default = "bulkloader_sns"
  type    = string
}

variable "protocol" {
  default = "email"
  type    = string
}

variable "acm_cert" {
  type = string
}

variable "license_path" {
  type = string
}

variable "password" {
  type = string
}