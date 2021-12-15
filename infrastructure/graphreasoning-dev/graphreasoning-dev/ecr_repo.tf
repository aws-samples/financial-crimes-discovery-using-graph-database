// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "aws_ecr_repository" "pre_rdfox_repo" {
  name = "pre-rdfox"
  image_tag_mutability = "IMMUTABLE"
  encryption_configuration {
    encryption_type = "KMS"
    kms_key = aws_kms_key.ecr_pre_rdfox.arn
  }
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "post_rdfox_repo" {
  name = "post-rdfox"
  image_tag_mutability = "IMMUTABLE"
  encryption_configuration {
    encryption_type = "KMS"
    kms_key = aws_kms_key.ecr_post_rdfox.arn
  }
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "custom_rdfox_repo" {
  name = "custom-rdfox"
  image_tag_mutability = "IMMUTABLE"
  encryption_configuration {
    encryption_type = "KMS"
    kms_key = aws_kms_key.ecr_custom_rdfox.arn
  }
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "data_generator_repo" {
  name = "data-generator"
  image_tag_mutability = "IMMUTABLE"
  encryption_configuration {
    encryption_type = "KMS"
    kms_key = aws_kms_key.ecr_custom_rdfox.arn
  }
  image_scanning_configuration {
    scan_on_push = true
  }
}

