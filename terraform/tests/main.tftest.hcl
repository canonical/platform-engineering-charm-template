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
    # renovate: depName="netbox-k8s"
    revision = 1
  }

  assert {
    condition     = output.app_name == "netbox-k8s"
    error_message = "netbox-k8s app_name did not match expected"
  }
}

run "integration_test" {
  variables {
    model_uuid = run.setup_tests.model_uuid
  }

  module {
    source = "./tests/integration_test"
  }

  assert {
    condition     = data.external.app_status.result.status == "blocked"
    error_message = "netbox-k8s app_name did not match expected"
  }
}
