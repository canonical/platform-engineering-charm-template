# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_providers {
    juju = {
      version = "~> 0.20.0"
      source  = "juju/juju"
    }
  }
}

provider "juju" {}

resource "juju_model" "testing" {
  name = "tf-testing-${formatdate("YYYYMMDDhhmmss", timestamp())}"
}

module "__charm_name__" {
  source     = "./.."
  model_uuid = juju_model.testing.uuid

  app_name = "__charm_name__"
  channel  = "latest/edge"

  # renovate: depName="__charm_name__"
  revision = 1
}
