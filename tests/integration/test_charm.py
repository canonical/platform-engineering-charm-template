#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests."""

import logging

import jubilant
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
def test_deploy(juju: jubilant.Juju, charm_path: str, resource_images: dict[str, str]):
    """
    arrange: A Juju model with MicroK8s.
    act: Deploy the charm with its OCI image resource.
    assert: The charm reaches active status.
    """
    juju.deploy(charm_path, resources=resource_images)
    juju.wait(jubilant.all_active)
