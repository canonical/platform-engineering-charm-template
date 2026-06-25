#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests."""

import logging
from pathlib import Path

import jubilant
import pytest
import yaml

logger = logging.getLogger(__name__)

CHARMCRAFT = yaml.safe_load(Path("./charmcraft.yaml").read_text())
RESOURCES = {name: val["upstream-source"] for name, val in CHARMCRAFT["resources"].items()}


@pytest.mark.abort_on_fail
def test_deploy(juju: jubilant.Juju, charm_path: str):
    """
    arrange: A Juju model with MicroK8s.
    act: Deploy the charm with its OCI image resource.
    assert: The charm reaches active status.
    """
    juju.deploy(charm_path, resources=RESOURCES)
    juju.wait(jubilant.all_active)
