# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for NetBox charm Prometheus integration."""

import logging

import jubilant
import pytest
import requests

from tests.integration.types import App

logger = logging.getLogger(__name__)


def test_prometheus_integration(
    netbox_app: App,
    juju: jubilant.Juju,
    prometheus_app: App,
    http: requests.Session,
):
    """
    arrange: after 12-Factor charm has been deployed.
    act: establish relations established with prometheus charm.
    assert: prometheus metrics endpoint for prometheus is active and prometheus has active scrape
        targets.
    """
    app = netbox_app
    metrics_port = 9102
    metrics_path = "/metrics"
    try:
        juju.integrate(app.name, prometheus_app.name)
        juju.wait(
            lambda status: jubilant.all_active(status, app.name, prometheus_app.name), delay=5
        )

        status = juju.status()
        prometheus_unit_ip = (
            status.apps[prometheus_app.name].units[prometheus_app.name + "/0"].address
        )
        app_unit_ip = status.apps[app.name].units[app.name + "/0"].address
        query_targets = http.get(
            f"http://{prometheus_unit_ip}:9090/api/v1/targets", timeout=10
        ).json()
        active_targets = query_targets["data"]["activeTargets"]
        assert len(active_targets)
        for active_target in active_targets:
            scrape_url = active_target["scrapeUrl"]
            if (
                str(metrics_port) in scrape_url
                and metrics_path in scrape_url
                and app_unit_ip in scrape_url
            ):
                # scrape the url directly to see if it works
                response = http.get(scrape_url, timeout=10)
                response.raise_for_status()
                break
        else:
            assert (
                False
            ), f"Application not scraped in port {metrics_port}. Scraped targets: {active_targets}"

    finally:
        juju.remove_relation(app.name, prometheus_app.name)
