#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for NetBox SAML integration."""

import logging

import jubilant
import pytest
import requests

from tests.integration.types import App

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("netbox_saml_integration")
def test_saml_integration(
    netbox_nginx_integration: App,
    juju: jubilant.Juju,
    saml_helper,
    netbox_hostname: str,
):
    """
    arrange: Integrate the NetBox Charm with saml-integrator, with a real SP.
    act: Call the endpoint to login with Saml.
    assert: User should be logged in.
    """
    saml_integrator_app_name = "saml-integrator"
    juju.wait(
        lambda status: jubilant.all_active(
            status, saml_integrator_app_name, netbox_nginx_integration.name
        ),
        timeout=600,
    )
    res = requests.get(
        "https://127.0.0.1/",
        headers={"Host": netbox_hostname},
        verify=False,
        timeout=30,
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
        url,
        data=saml_response.data,
        headers={"Host": netbox_hostname},
        timeout=10,
        verify=False,
    )
    assert logged_in_page.status_code == 200
    assert "<title>Home | NetBox</title>" in logged_in_page.text
    # The user is logged in.
    assert "Log Out" in logged_in_page.text
    assert "ubuntu" in logged_in_page.text
    assert "ubuntu" in logged_in_page.text
