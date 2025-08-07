# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "channel" {
  description = "The channel to use when deploying a charm."
  type        = string
  default     = "latest/edge"
}

variable "revision" {
  description = "Revision number of the charm."
  type        = number
  default     = null
}

terraform {
  required_providers {
    juju = {
      version = "~> 0.20.0"
      source  = "juju/juju"
    }
  }
}

provider "juju" {}

module "charm_name" {
  source   = "./.."
  app_name = "charm_name"
  channel  = var.channel
  model    = "prod-charm_name-example"
  revision = var.revision
}
