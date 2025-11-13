# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more about testing at: https://ops.readthedocs.io/en/latest/explanation/testing.html

"""Unit tests."""

import typing

import ops
import ops.testing

from charm import Charm


def test_reconcile_on_install():
    """
    arrange: Initial state with valid configuration.
    act: Run install hook.
    assert: The unit is active.
    """
    context = ops.testing.Context(
        charm_type=Charm,
    )
    base_state: dict[str, typing.Any] = {
        "config": {"log-level": "info"},
    }
    state_in = ops.testing.State(**base_state)
    state_out = context.run(context.on.install(), state_in)
    assert state_out.unit_status == ops.testing.ActiveStatus()


def test_reconcile_on_start():
    """
    arrange: Initial state with valid configuration.
    act: Run start hook.
    assert: The unit is active.
    """
    context = ops.testing.Context(
        charm_type=Charm,
    )
    base_state: dict[str, typing.Any] = {
        "config": {"log-level": "debug"},
    }
    state_in = ops.testing.State(**base_state)
    state_out = context.run(context.on.start(), state_in)
    assert state_out.unit_status == ops.testing.ActiveStatus()


def test_reconcile_on_config_changed_valid():
    """
    arrange: State with valid config change.
    act: Run config_changed hook (which calls reconcile).
    assert: The unit is active and configuration is applied.
    """
    context = ops.testing.Context(
        charm_type=Charm,
    )
    base_state: dict[str, typing.Any] = {
        "config": {"log-level": "debug"},
    }
    state_in = ops.testing.State(**base_state)
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status == ops.testing.ActiveStatus()


def test_reconcile_on_config_changed_invalid():
    """
    arrange: State with invalid config.
    act: Run config_changed hook.
    assert: The unit is blocked due to invalid configuration.
    """
    context = ops.testing.Context(
        charm_type=Charm,
    )
    base_state: dict[str, typing.Any] = {
        "config": {"log-level": "foobar"},
    }
    state_in = ops.testing.State(**base_state)
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.testing.BlockedStatus().name
