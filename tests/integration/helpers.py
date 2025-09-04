# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper functions for integration tests."""

import logging
import secrets
import string

import jubilant
import requests

from tests.integration.types import App

logger = logging.getLogger(__name__)


def get_new_admin_token(juju: jubilant.Juju, netbox_app: App, netbox_base_url: str) -> str:
    """Create an admin token for NetBox.

    Args:
        juju: Juju instance.
        netbox_app: NetBox app. Necessary to create the superuser
        netbox_base_url: NetBox base url. Needed to get token from superuser.

    Returns:
        The new admin token
    """
    # Create a superuser
    username = "".join((secrets.choice(string.ascii_letters) for i in range(8)))
    action_create_user = juju.run(
        f"{netbox_app.name}/0",
        "create-superuser",
        {"username": username, "email": "admin@example.com"},
    )
    assert action_create_user.status == "completed"
    password = action_create_user.results["password"]

    # Get a token to work with the API
    url = f"{netbox_base_url}/api/users/tokens/provision/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    res = requests.post(
        url,
        json={"username": username, "password": password},
        timeout=5,
        headers=headers,
    )
    assert res.status_code == 201
    token = res.json()["key"]
    logger.info("Admin Token: %s", token)
    return token
