# Optional AWS infrastructure

This is an independent Terraform example for the cloud portion of the lab. It has not been deployed. The local demo does not need AWS and no cloud resources are created by GitHub Actions.

The template creates an Ubuntu EC2 instance in a subnet you provide, encrypted EBS storage, a private versioned S3 bucket and an EC2 role scoped to a backup object prefix. The instance has no public IP and no inbound security group rules. It is a design example, not a complete production deployment or a remotely managed server. A real environment would need an approved private management path, DNS and recovery architecture.

## Review before applying

Terraform, an AWS account with appropriate permissions, and an existing VPC/subnet are required. AWS resources can incur charges. Use a separate sandbox account and check pricing first.

```bash
cd aws
terraform init
terraform fmt -check
terraform validate
terraform plan -var="aws_region=ca-central-1" -var="vpc_id=vpc-REPLACE" -var="subnet_id=subnet-REPLACE" -var="backup_bucket=globally-unique-replace"
```

Replace all placeholders. Do not apply against an employer's account. Review tags, network configuration and costs before running terraform apply. No SSH access is configured; set up an approved management method before using the host. Do not place credentials or real backups in the repository.

When finished, remove any objects and object versions from the dedicated sandbox bucket if appropriate, then destroy the lab resources with the same variables. The bucket deliberately has force_destroy disabled.
