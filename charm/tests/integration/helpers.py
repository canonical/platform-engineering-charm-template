# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper functions for integration tests."""

import asyncio
import datetime
import logging
import secrets
import string
import typing

import pytest
import requests
from juju.action import Action
from juju.application import Application

logger = logging.getLogger(__name__)


async def assert_return_true_with_retry(
    fn: typing.Callable[[], bool], delay: int = 10, timeout: int = 300
) -> None:
    """Assert that the function fn returns True before the timeout.

    The function will be invoked until timeout. Between invocations,
    a sleep of delay seconds will occur. If the function returns True, this
    function will return, otherwise it will fail using pytest.fail.

    Args:
        fn: function to run until timeout.
        delay: time delay between fn invocations.
        timeout: after timeout this function fails with pytest.fail.
    """
    start_time = datetime.datetime.now()
    timeoutdelta = datetime.timedelta(seconds=timeout)

    while True:
        res = fn()
        if res:
            break
        if datetime.datetime.now() - start_time > timeoutdelta:
            pytest.fail("Function timeout.")
        await asyncio.sleep(delay)


async def get_new_admin_token(netbox_app: Application, netbox_base_url: str):
    """Create an admin token for Netbox.

    Args:
        netbox_app: netbox app. Necessary to create the superuser
        netbox_base_url: NetBox base url. Needed to get token from superuser.

    Returns:
        The new admin token
    """
    # Create a superuser
    username = "".join((secrets.choice(string.ascii_letters) for i in range(8)))
    action_create_user: Action = await netbox_app.units[0].run_action(  # type: ignore
        "create-superuser", username=username, email="admin@example.com"
    )
    await action_create_user.wait()
    assert action_create_user.status == "completed"
    password = action_create_user.results["password"]

    # Get a token to work with the API
    url = f"{netbox_base_url}/api/users/tokens/provision/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    res = requests.post(
        url, json={"username": username, "password": password}, timeout=5, headers=headers
    )
    assert res.status_code == 201
    token = res.json()["key"]
    logger.info("Admin Token: %s", token)
    return token


async def get_unit_ips(application: Application) -> list[str]:
    """Get ip addresses of all units of an application.

    Args:
        application: Application instance.

    Returns:
        all the unit ips
    """
    status = await application.model.get_status()
    return [
        unit.address  # type: ignore
        for unit in status.applications[application.name].units.values()  # type: ignore
    ]
