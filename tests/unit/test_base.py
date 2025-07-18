# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more about testing at: https://ops.readthedocs.io/en/latest/explanation/testing.html

# pylint: disable=duplicate-code,missing-function-docstring
"""Unit tests."""

import unittest

import ops
import ops.testing

from charm import IsCharmsTemplateCharm


class TestCharm(unittest.TestCase):
    """Test class."""

    def setUp(self):
        """Set up the testing environment."""
        self.harness = ops.testing.Harness(IsCharmsTemplateCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_httpbin_pebble_ready(self):
        # Expected plan after Pebble ready with default config
        expected_plan = {
            "services": {
                "httpbin": {
                    "override": "replace",
                    "summary": "httpbin",
                    "command": "gunicorn -b 0.0.0.0:80 httpbin:app -k gevent",
                    "startup": "enabled",
                    "environment": {"GUNICORN_CMD_ARGS": "--log-level info"},
                }
            },
        }
        # Simulate the container coming up and emission of pebble-ready event
        self.harness.container_pebble_ready("httpbin")
        # Get the plan now we've run PebbleReady
        updated_plan = self.harness.get_container_pebble_plan("httpbin").to_dict()
        # Check we've got the plan we expected
        self.assertEqual(expected_plan, updated_plan)
        # Check the service was started
        service = self.harness.model.unit.get_container("httpbin").get_service("httpbin")
        self.assertTrue(service.is_running())
        # Ensure we set an ActiveStatus with no message
        self.assertEqual(self.harness.model.unit.status, ops.ActiveStatus())

    def test_config_changed_valid_can_connect(self):
        # Ensure the simulated Pebble API is reachable
        self.harness.set_can_connect("httpbin", True)
        # Trigger a config-changed event with an updated value
        self.harness.update_config({"log-level": "debug"})
        # Get the plan now we've run PebbleReady
        updated_plan = self.harness.get_container_pebble_plan("httpbin").to_dict()
        updated_env = updated_plan["services"]["httpbin"]["environment"]
        # Check the config change was effective
        self.assertEqual(updated_env, {"GUNICORN_CMD_ARGS": "--log-level debug"})
        self.assertEqual(self.harness.model.unit.status, ops.ActiveStatus())

    def test_config_changed_valid_cannot_connect(self):
        # Trigger a config-changed event with an updated value
        self.harness.update_config({"log-level": "debug"})
        # Check the charm is in WaitingStatus
        self.assertIsInstance(self.harness.model.unit.status, ops.WaitingStatus)

    def test_config_changed_invalid(self):
        # Ensure the simulated Pebble API is reachable
        self.harness.set_can_connect("httpbin", True)
        # Trigger a config-changed event with an updated value
        self.harness.update_config({"log-level": "foobar"})
        # Check the charm is in BlockedStatus
        self.assertIsInstance(self.harness.model.unit.status, ops.BlockedStatus)
