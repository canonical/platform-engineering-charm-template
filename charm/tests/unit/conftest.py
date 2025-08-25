# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for NetBox operator charm unit tests."""

import textwrap

import pytest
from ops.testing import Harness

import charm


@pytest.fixture(scope="function", name="harness")
def harness_fixture():
    """Enable ops test framework harness.

    Yields:
       Harness fixture
    """
    # The real configuration files are created by expanding
    # the extension 'django-framework'. However, this is not
    # supported by ops.testing. An alternative to setting it here
    # would be to call `charmcraft expand-extensions`.
    meta_file = textwrap.dedent(
        """\
name: netbox
type: charm
containers:
  django-app:
    resource: django-app-image
peers:
  secret-storage:
    interface: secret-storage
provides:
  grafana-dashboard:
    interface: grafana_dashboard
  metrics-endpoint:
    interface: prometheus_scrape
requires:
  ingress:
    interface: ingress
    limit: 1
  logging:
    interface: loki_push_api
  postgresql:
    interface: postgresql_client
    limit: 1
  redis:
    interface: redis
    limit: 1
  saml:
    interface: saml
    limit: 1
    optional: true
  s3:
    interface: s3
    limit: 1
resources:
  django-app-image:
     type: oci-image
"""
    )

    actions_file = textwrap.dedent(
        """\
    create-superuser:
      email:
        type: string
      username:
        type: string
    rotate-secret-key:
"""
    )

    harness = Harness(charm.DjangoCharm, meta=meta_file, actions=actions_file)

    yield harness

    harness.cleanup()
