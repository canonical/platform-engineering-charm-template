# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the NetBox charm."""
import logging
import secrets
import string

import jubilant
import pytest
import requests
from juju.application import Application
from saml_test_helper import SamlK8sTestHelper

from charm.tests.integration.types import App
from tests.integration.helpers import (
    assert_return_true_with_retry,
    get_new_admin_token,
    get_unit_ips,
)

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

        # Also  some random thing from the static dir.
        url = f"http://{unit.address}:8000/static/netbox.ico"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200


@pytest.mark.usefixtures("netbox_app")
@pytest.mark.usefixtures("s3_netbox_bucket")
async def test_netbox_storage(
    netbox_app: Application,
    s3_netbox_configuration: dict,
    boto_s3_client,
) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Create a site and post an image
    assert: The site is created and there is an extra object (the image)
        in S3.
    """
    unit_ip = (await get_unit_ips(netbox_app))[0]
    base_url = f"http://{unit_ip}:8000"
    token = await get_new_admin_token(netbox_app, base_url)

    # Save the current number of objects in the S3 bucket.
    bucket_name = s3_netbox_configuration["bucket"]
    boto_res = boto_s3_client.list_objects_v2(Bucket=bucket_name)
    previous_keycount = boto_res["KeyCount"]

    # Create a site.
    headers_with_auth = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"TOKEN {token}",
    }
    url = f"{base_url}/api/dcim/sites/"
    site = {
        "name": "".join((secrets.choice(string.ascii_lowercase) for i in range(5))),
        "slug": "".join((secrets.choice(string.ascii_lowercase) for i in range(5))),
    }
    res = requests.post(url, json=site, timeout=5, headers=headers_with_auth)
    assert res.status_code == 201
    site_id = res.json()["id"]

    # Post an image to the site previously created.
    url = f"{base_url}/api/extras/image-attachments/"
    # A one pixel image.
    smallpngimage = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00"
        b"\x007n\xf9$\x00\x00\x00\nIDATx\x01c`\x00\x00\x00\x02\x00\x01su\x01\x18\x00\x00\x00"
        b"\x00IEND\xaeB`\x82"
    )
    files = {"image": ("image.png", smallpngimage)}
    payload = {
        "object_type": "dcim.site",
        "object_id": site_id,
        "name": "image name",
        "image_height": 1,
        "image_width": 1,
    }
    res = requests.post(
        url, files=files, data=payload, timeout=5, headers={"Authorization": f"TOKEN {token}"}
    )
    assert res.status_code == 201

    # check that there is a new file in S3.
    bucket_name = s3_netbox_configuration["bucket"]
    boto_res = boto_s3_client.list_objects_v2(Bucket=bucket_name)
    assert boto_res["KeyCount"] == previous_keycount + 1


@pytest.mark.usefixtures("netbox_app")
async def test_netbox_rq_worker_running(netbox_app: Application) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Do a get request to the status api.
    assert: Check that there is one rq worker running.
    """
    unit_ips = await get_unit_ips(netbox_app)
    for unit_ip in unit_ips:
        url = f"http://{unit_ip}:8000/api/status/"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert res.json()["rq-workers-running"] == 1


@pytest.mark.usefixtures("s3_netbox_bucket")
@pytest.mark.usefixtures("netbox_app")
async def test_netbox_check_cronjobs(
    netbox_app: Application,
    s3_netbox_credentials: dict,
    s3_netbox_configuration: dict,
) -> None:
    """
    arrange: Build and deploy the NetBox charm. Create a superuser and get its token.
    act: Create a s3 data source.
    assert: The cron task syncdatasource should update the status of the datasource
        to completed.
    """
    unit_ip = (await get_unit_ips(netbox_app))[0]
    base_url = f"http://{unit_ip}:8000"
    token = await get_new_admin_token(netbox_app, base_url)
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
    def check_data_source_updated() -> bool:
        """Check that the data source gets updated.

        Returns:
           Whether the function succeeded or not.
        """
        url = f"{base_url}/api/core/data-sources/{data_source_id}/"
        res = requests.get(url, timeout=5, headers=headers_with_auth)
        assert res.status_code == 200
        logger.info("current datasource status: %s", res.json()["status"])
        if res.json()["status"]["value"] == "completed":
            return True
        return False

    # Adjust the timeout to the schedule for the syncdatasource cron task
    await assert_return_true_with_retry(check_data_source_updated, delay=10, timeout=350)


@pytest.mark.usefixtures("netbox_nginx_integration")
@pytest.mark.usefixtures("netbox_saml_integration")
async def test_saml_netbox(
    saml_helper: SamlK8sTestHelper,
    netbox_hostname: str,
) -> None:
    """
    arrange: Deploy NetBox with nginx and saml. Check that the
        user ubuntu is not logged in.
    act: Log in with saml in NetBox.
    assert: Check that the user ubuntu is logged in.
    """
    res = requests.get(
        "https://127.0.0.1/",
        headers={"Host": netbox_hostname},
        verify=False,
        timeout=30,  # nosec
    )
    assert res.status_code == 200
    assert "<title>Home | NetBox</title>" in res.text
    # The user is not logged in.
    assert "Log Out" not in res.text
    assert "ubuntu" not in res.text

    session = requests.session()

    # Act part. Log in with SAML.
    redirect_url = "https://127.0.0.1/oauth/login/saml/?next=%2F&idp=saml"
    res = session.get(
        redirect_url,
        headers={"Host": netbox_hostname},
        timeout=5,
        verify=False,
        allow_redirects=False,
    )
    assert res.status_code == 302
    redirect_url = res.headers["Location"]
    saml_response = saml_helper.redirect_sso_login(redirect_url)
    assert f"https://{netbox_hostname}" in saml_response.url

    # Assert part. Check that the user is logged in.
    url = saml_response.url.replace(f"https://{netbox_hostname}", "https://127.0.0.1")
    logged_in_page = session.post(
        url, data=saml_response.data, headers={"Host": netbox_hostname}, timeout=10, verify=False
    )
    assert logged_in_page.status_code == 200
    assert "<title>Home | NetBox</title>" in logged_in_page.text
    # The user is logged in.
    assert "Log Out" in logged_in_page.text
    assert "ubuntu" in logged_in_page.text
