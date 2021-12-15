// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


data "aws_ami" "al2" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-2.0.20210525.0-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["137112412989"] # Amazon
}

resource "aws_iam_instance_profile" "bastion_profile" {
  name = "bastion_profile2"
  role = var.role
}

resource "aws_instance" "instance" {
  ami                    = data.aws_ami.al2.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet
  vpc_security_group_ids = [var.security_group]
  key_name               = var.public_key
  iam_instance_profile   = aws_iam_instance_profile.bastion_profile.id
  tags = {
    Name = "bastion"
  }
}

output "bastion_public_hostname" {
  value = aws_instance.instance.public_dns
}
