# =============================================================================
# Solar PV LLM AI - Terraform Infrastructure
# Supports AWS, GCP, and Azure
# =============================================================================

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  # Backend configuration for state management
  backend "s3" {
    bucket         = "solar-pv-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "solar-pv-terraform-locks"
  }
}

# =============================================================================
# Variables
# =============================================================================

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "solar-pv-llm-ai"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
}

# =============================================================================
# Providers
# =============================================================================

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "Solar-PV-LLM-AI"
      ManagedBy   = "Terraform"
    }
  }
}

# =============================================================================
# Data Sources
# =============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

# =============================================================================
# Modules
# =============================================================================

module "vpc" {
  source = "./modules/vpc"

  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = slice(data.aws_availability_zones.available.names, 0, 3)
}

module "eks" {
  source = "./modules/eks"

  environment        = var.environment
  cluster_name       = var.cluster_name
  cluster_version    = var.cluster_version
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
}

module "rds" {
  source = "./modules/rds"

  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.database_subnet_ids
  instance_class      = var.database_instance_class
  allocated_storage   = 100
  database_name       = "solar_pv_db"
  master_username     = "solar_pv_admin"
}

module "elasticache" {
  source = "./modules/elasticache"

  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  node_type   = var.redis_node_type
}

module "s3" {
  source = "./modules/s3"

  environment = var.environment
  buckets = [
    "solar-pv-models",
    "solar-pv-data",
    "solar-pv-backups"
  ]
}

module "monitoring" {
  source = "./modules/monitoring"

  environment  = var.environment
  cluster_name = var.cluster_name
}

# =============================================================================
# Outputs
# =============================================================================

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

output "s3_buckets" {
  description = "S3 bucket names"
  value       = module.s3.bucket_names
}
