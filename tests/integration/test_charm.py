# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the NetBox charm."""

import logging
import secrets
import string

import jubilant
import pytest
import requests
from tenacity import retry, stop_after_delay, wait_fixed

from tests.integration.helpers import get_new_admin_token
from tests.integration.types import App

logger = logging.getLogger(__name__)


def test_netbox_health(netbox_app: App, juju: jubilant.Juju) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Do a get request to the main page and to an asset.
    assert: Both return 200 and the page contains the correct title.
    """
    status = juju.status()
    assert status.apps[netbox_app.name].units[netbox_app.name + "/0"].is_active
    for unit in status.apps[netbox_app.name].units.values():
        url = f"http://{unit.address}:8000"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert b"<title>Home | NetBox</title>" in res.content

        # Also some random thing from the static dir.
        url = f"http://{unit.address}:8000/static/netbox.ico"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200


@pytest.mark.usefixtures("netbox_app")
def test_netbox_rq_worker_running(juju: jubilant.Juju, netbox_app: App) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Do a get request to the status api.
    assert: Check that there is one rq worker running.
    """
    status = juju.status()
    for unit in status.apps[netbox_app.name].units.values():
        url = f"http://{unit.address}:8000/api/status/"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert res.json()["rq-workers-running"] == 1


@pytest.mark.usefixtures("netbox_app")
def test_netbox_check_cronjobs(
    juju: jubilant.Juju,
    netbox_app: App,
    s3_netbox_credentials: dict,
    s3_netbox_configuration: dict,
) -> None:
    """
    arrange: Build and deploy the NetBox charm. Create a superuser and get its token.
    act: Create a s3 data source.
    assert: The cron task syncdatasource should update the status of the datasource
        to completed.
    """
    unit_ip = juju.status().apps[netbox_app.name].units[netbox_app.name + "/0"].address
    base_url = f"http://{unit_ip}:8000"
    token = get_new_admin_token(juju, netbox_app, base_url)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Create a datasource
    headers_with_auth = headers | {"Authorization": f"TOKEN {token}"}
    url = f"{base_url}/api/core/data-sources/"
    data_source_name = "".join((secrets.choice(string.ascii_letters) for i in range(8)))
    data_source = {
        "name": data_source_name,
        "source_url": f"{s3_netbox_configuration['endpoint']}/{s3_netbox_configuration['bucket']}",
        "type": "amazon-s3",
        "description": "description",
        "parameters": {
            "aws_access_key_id": s3_netbox_credentials["access-key"],
            "aws_secret_access_key": s3_netbox_credentials["secret-key"],
        },
    }
    res = requests.post(url, json=data_source, timeout=5, headers=headers_with_auth)
    assert res.status_code == 201
    data_source_id = res.json()["id"]

    # The cron task for the syncdatasource should update the datasource status to completed.
    @retry(
        stop=stop_after_delay(350),
        wait=wait_fixed(10),
    )
    def check_data_source_updated():
        """Check that the data source gets updated."""
        url = f"{base_url}/api/core/data-sources/{data_source_id}/"
        res = requests.get(url, timeout=5, headers=headers_with_auth)
        assert res.status_code == 200
        logger.info("current datasource status: %s", res.json()["status"])
        assert res.json()["status"]["value"] == "completed"

    check_data_source_updated()
