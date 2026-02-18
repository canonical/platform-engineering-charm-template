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

# Add some specific tests here, like integrations

# tflint-ignore: terraform_unused_declarations
data "external" "app_status" {
  program = ["bash", "${path.module}/wait-for-active.sh", var.model_uuid, "__charm_name__"]

  #depends_on = [
  #  juju_integration....
  #]
}
