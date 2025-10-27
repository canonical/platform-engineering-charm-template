#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests."""

import logging

import jubilant
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
def test_simple_relay(juju: jubilant.Juju, app_name: str):
    """
    arrange:
    act:
    assert:
    """
    status = juju.status()
    unit = list(status.apps[app_name].units.values())[0]
    assert unit
