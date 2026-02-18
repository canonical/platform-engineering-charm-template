# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">= 1.0"
  required_providers {
    external = {
      version = "> 2"
      source  = "hashicorp/external"
    }
    juju = {
      version = "> 1.1.0"
      source  = "juju/juju"
    }
  }
}

provider "juju" {}

variable "model_uuid" {
  type = string
}

resource "juju_application" "redis" {
  model_uuid = var.model_uuid
  charm {
    base    = "ubuntu@22.04"
    channel = "latest/edge"
    name    = "redis-k8s"
  }
}

resource "juju_integration" "redis" {
  model_uuid = var.model_uuid

  application {
    name = "netbox-k8s"
  }

  application {
    name = juju_application.redis.name
  }
}

# tflint-ignore: terraform_unused_declarations
data "external" "app_status" {
  program = ["bash", "${path.module}/wait-for-active.sh", var.model_uuid, "netbox-k8s", "3m"]

  depends_on = [
    juju_integration.redis
  ]
}
