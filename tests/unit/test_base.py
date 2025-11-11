# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more about testing at: https://ops.readthedocs.io/en/latest/explanation/testing.html

"""Unit tests."""

import typing

import ops
import ops.testing

from charm import TemplateCharm


def test_active_on_httpbin_pebble_ready():
    """
    arrange: State with the container httpbin.
    act: Run httpbin_pebble_ready hook.
    assert: The unit is active and the httpbin container service is active.
    """
    context = ops.testing.Context(
        charm_type=TemplateCharm,
    )
    container = ops.testing.Container(name="httpbin", can_connect=True)  # type: ignore[call-arg]
    base_state: dict[str, typing.Any] = {
        "config": {"log-level": "info"},
        "containers": {container},
    }
    state_in = ops.testing.State(**base_state)
    state_out = context.run(context.on.pebble_ready(container), state_in)
    assert state_out.unit_status == ops.testing.ActiveStatus()
    # Check the service was started:
    assert (
        state_out.get_container(container.name).service_statuses["httpbin"]
        == ops.pebble.ServiceStatus.ACTIVE
    )


def test_config_changed_invalid():
    """
    arrange: State with the container httpbin. The config option log-level is invalid.
    act: Run config_changed hook.
    assert: The unit is blocked.
    """
    context = ops.testing.Context(
        charm_type=TemplateCharm,
    )
    container = ops.testing.Container(name="httpbin", can_connect=True)  # type: ignore[call-arg]
    base_state: dict[str, typing.Any] = {
        "config": {"log-level": "foobar"},
        "containers": {container},
    }
    state_in = ops.testing.State(**base_state)
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.testing.BlockedStatus().name
