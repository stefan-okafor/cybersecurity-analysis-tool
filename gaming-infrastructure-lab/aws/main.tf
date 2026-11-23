terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "gaming-infrastructure-lab"
      Environment = "sandbox"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "ca-central-1"
}
variable "vpc_id" {
  type = string
}
variable "subnet_id" {
  type = string
}
variable "backup_bucket" {
  type = string
}
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_s3_bucket" "backups" {
  bucket        = var.backup_bucket
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket                  = aws_s3_bucket.backups.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_iam_role" "server" {
  name_prefix = "gaming-lab-server-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "backup_objects" {
  role = aws_iam_role.server.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${aws_s3_bucket.backups.arn}/gaming-lab/*"
    }]
  })
}

resource "aws_iam_instance_profile" "server" {
  name_prefix = "gaming-lab-"
  role        = aws_iam_role.server.name
}

resource "aws_security_group" "server" {
  name_prefix = "gaming-lab-"
  description = "No inbound access; HTTPS outbound for approved services"
  vpc_id      = var.vpc_id
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  associate_public_ip_address = false
  vpc_security_group_ids      = [aws_security_group.server.id]
  iam_instance_profile        = aws_iam_instance_profile.server.name

  metadata_options {
    http_tokens = "required"
  }
  root_block_device {
    encrypted = true
    volume_type = "gp3"
    volume_size = 12
  }
  tags = {
    Name = "gaming-lab-server"
  }
}

output "backup_bucket" {
  value = aws_s3_bucket.backups.id
}
output "private_instance_id" {
  value = aws_instance.server.id
}
