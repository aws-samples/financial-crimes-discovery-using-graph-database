// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


variable "namespace" {
  type = string
}


variable "rdfox_access_security_group" {
  type = string
}

variable "rdfox_port" {
  type = number
}

variable "security_group" {
  type = string
}

variable "rdfox_service_account" {
  type = string
}

variable "persistent_replicas" {
  type    = number
  default = 0
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
