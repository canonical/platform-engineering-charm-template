#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the NetBox S3 integration."""

import logging
import secrets
import string

import jubilant
import pytest
import requests
from minio import Minio

from tests.integration.helpers import get_new_admin_token
from tests.integration.types import App

logger = logging.getLogger(__name__)

# Pylint thinks there are too many local variables, but that's not true.
# pylint: disable=too-many-locals


@pytest.mark.usefixtures("s3_integrator_app")
def test_netbox_storage(
    netbox_app: App,
    s3_netbox_configuration: dict,
    minio_app: App,
    s3_netbox_credentials: dict,
    juju: jubilant.Juju,
) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Create a site and post an image
    assert: The site is created and there is an extra object (the image)
        in S3.
    """
    status = juju.status()
    minio_ip = status.apps[minio_app.name].units[minio_app.name + "/0"].address
    unit_ip = status.apps[netbox_app.name].units[netbox_app.name + "/0"].address

    minio_client = Minio(
        f"{minio_ip}:9000",
        access_key=s3_netbox_credentials["access-key"],
        secret_key=s3_netbox_credentials["secret-key"],
        secure=False,
    )
    juju.wait(
        jubilant.all_active,
        timeout=600,
    )
    base_url = f"http://{unit_ip}:8000"
    token = get_new_admin_token(juju, netbox_app, base_url)

    # Save the current number of objects in the S3 bucket.
    bucket_name = s3_netbox_configuration["bucket"]
    object_list = list(minio_client.list_objects(bucket_name=bucket_name))
    previous_keycount = len(object_list) if object_list else 0

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
        url,
        files=files,
        data=payload,
        timeout=5,
        headers={"Authorization": f"TOKEN {token}"},
    )
    assert res.status_code == 201

    # check that there is a new file in S3.
    key_count = len(list(minio_client.list_objects(bucket_name=bucket_name)))
    assert key_count == previous_keycount + 1
