# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper functions for integration tests."""

import logging
import secrets
import string

import jubilant
import requests

from tests.integration.types import App
from tenacity import retry, stop_after_attempt, wait_exponential, wait_fixed

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


@retry(stop=stop_after_attempt(5), wait=wait_fixed(5))
def check_grafana_datasource_types_patiently(
    grafana_session: requests.session,
    grafana_ip: str,
    expected_datasource_types: list[str],
):
    """Get datasources directly from Grafana REST API, but also try multiple times."""
    url = f"http://{grafana_ip}:3000/api/datasources"
    datasources = grafana_session.get(url, timeout=10).json()
    datasource_types = set(datasource["type"] for datasource in datasources)
    for datasource in expected_datasource_types:
        assert datasource in datasource_types, f"Datasource type {datasource} not found in Grafana"


@retry(stop=stop_after_attempt(5), wait=wait_fixed(15))
def check_grafana_dashboards_patiently(
    grafana_session: requests.session, grafana_ip: str, dashboard: str
):
    """Check if dashboard can be found in Grafana directly from Grafana REST API,
    but also try multiple times."""
    dashboards = grafana_session.get(
        f"http://{grafana_ip}:3000/api/search",
        timeout=10,
        params={"query": dashboard},
    ).json()
    assert len(dashboards)
