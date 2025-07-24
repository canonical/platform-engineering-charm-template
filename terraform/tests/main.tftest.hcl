# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variables {
  channel = "latest/edge"
  # renovate: depName="charm_name"
  revision = 1
}

run "basic_deploy" {
  assert {
    condition     = module.charm_name.app_name == "charm_name"
    error_message = "charm_name app_name did not match expected"
  }
}
