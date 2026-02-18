# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

run "setup_tests" {
  module {
    source = "./tests/setup"
  }
}

run "basic_deploy" {
  variables {
    model_uuid = run.setup_tests.model_uuid
    channel    = "latest/edge"
    # renovate: depName="__charm_name__"
    revision = 1
  }

  assert {
    condition     = output.app_name == "__charm_name__"
    error_message = "__charm_name__ app_name did not match expected"
  }
}
