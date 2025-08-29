# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the NetBox charm integration tests."""

import logging
import os.path
from collections.abc import Generator
from typing import cast

import jubilant
import pytest
from minio import Minio
from pytest import Config
from saml_test_helper import SamlK8sTestHelper

from tests.conftest import NETBOX_IMAGE_PARAM
from tests.integration.types import App

logger = logging.getLogger(__name__)

# caused by pytest fixtures, mark does not work in fixtures
# pylint: disable=too-many-arguments, unused-argument


@pytest.fixture(scope="module", name="saml_app_name")
def saml_app_name_fixture() -> str:
    """Return the name of the saml-integrator application deployed for tests."""
    return "saml-integrator"


@pytest.fixture(scope="module", name="nginx_app_name")
def nginx_app_name_fixture() -> str:
    """Return the name of the nginx-ingress-integrator application deployed for tests."""
    return "nginx-ingress-integrator"


@pytest.fixture(scope="module", name="postgresql_app_name")
def postgresql_app_name_fixture() -> str:
    """Return the name of the postgresql application deployed for tests."""
    return "postgresql-k8s"


@pytest.fixture(scope="module", name="s3_integrator_app_name")
def s3_integrator_app_name_fixture() -> str:
    """Return the name of the s3-integrator application deployed for tests."""
    return "s3-integrator"


@pytest.fixture(scope="module", name="netbox_app_name")
def netbox_app_name_fixture() -> str:
    """Return the name of the netbox application deployed for tests."""
    return "netbox"


@pytest.fixture(scope="module", name="netbox_hostname")
def netbox_hostname_fixture() -> str:
    """Return the name of the netbox hostname used for tests."""
    return "netbox.internal"


@pytest.fixture(scope="module", name="redis_app_name")
def redis_app_name_fixture() -> str:
    """Return the name of the redis application deployed for tests."""
    return "redis-k8s"


@pytest.fixture(scope="module", name="netbox_app_image")
def netbox_app_image_fixture(pytestconfig: Config) -> str:
    """Get value from parameter netbox-image."""
    netbox_app_image = pytestconfig.getoption(NETBOX_IMAGE_PARAM)
    assert netbox_app_image, f"{NETBOX_IMAGE_PARAM} must be set"
    return netbox_app_image


@pytest.fixture(scope="module", name="netbox_charm")
def netbox_charm_fixture(pytestconfig: Config) -> str:
    """Get value from parameter charm-file."""
    charm = pytestconfig.getoption("--charm-file")
    assert charm, "--charm-file must be set"
    if not os.path.exists(charm):
        logger.info("Using parent directory for charm file")
        charm = os.path.join("..", charm)
    return charm


@pytest.fixture(scope="module", name="saml_helper")
def saml_helper_fixture(
    juju: jubilant.Juju,
) -> SamlK8sTestHelper:
    """Fixture for SamlHelper."""
    model_name = juju.status().model.name
    saml_helper = SamlK8sTestHelper.deploy_saml_idp(model_name)
    return saml_helper


@pytest.fixture(scope="module", name="saml_app")
def saml_app_fixture(
    juju: jubilant.Juju,
    saml_app_name: str,
) -> App:
    """Deploy saml."""
    if juju.status().apps.get(saml_app_name):
        logger.info(f"{saml_app_name} already deployed")
        return App(saml_app_name)
    juju.deploy(
        saml_app_name,
        channel="latest/edge",
    )
    return App(saml_app_name)


@pytest.fixture(scope="module", name="netbox_saml_integration")
def netbox_saml_integration_fixture(
    juju: jubilant.Juju,
    saml_app: App,
    netbox_app: App,
    netbox_hostname: str,
    saml_helper: SamlK8sTestHelper,
):
    """Integrate Netbox and SAML for saml integration."""
    juju.config(
        netbox_app.name,
        {
            "saml-sp-entity-id": f"https://{netbox_hostname}",
            # The saml Name for FriendlyName "uid"
            "saml-username": "urn:oid:0.9.2342.19200300.100.1.1",
        },
    )
    model_name = juju.status().model.name
    try:
        saml_helper.prepare_pod(model_name, f"{saml_app.name}-0")
        saml_helper.prepare_pod(model_name, f"{netbox_app.name}-0")
    except Exception as e:
        if "already exists" in str(e):
            logger.info("Pod already prepared")
        else:
            raise
    juju.config(
        saml_app.name,
        {
            "entity_id": f"https://{saml_helper.SAML_HOST}/metadata",
            "metadata_url": f"https://{saml_helper.SAML_HOST}/metadata",
        },
    )
    juju.config(
        netbox_app.name,
        {
            "saml-sp-entity-id": f"https://{netbox_hostname}",
            # The saml Name for FriendlyName "uid"
            "saml-username": "urn:oid:0.9.2342.19200300.100.1.1",
        },
    )
    try:
        juju.integrate(saml_app.name, netbox_app.name)
    except Exception as e:
        if "already exists" in str(e):
            logger.info("Relation already exists")
        else:
            raise
    juju.wait(
        lambda status: jubilant.all_active(status, saml_app.name, netbox_app.name), timeout=10 * 60
    )

    # For the saml_helper, a SAML XML metadata for the service is needed.
    # There are instructions to generate it in:
    # https://python-social-auth.readthedocs.io/en/latest/backends/saml.html#basic-usage.
    # This one is instead a minimalistic one that works for the test.
    metadata_xml = """
    <md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" cacheDuration="P10D"
                         entityID="https://netbox.internal">
      <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
                          AuthnRequestsSigned="false" WantAssertionsSigned="true">
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                     Location="https://netbox.internal/oauth/complete/saml/"
                                     index="1"/>
      </md:SPSSODescriptor>
    </md:EntityDescriptor>
    """
    try:
        saml_helper.register_service_provider(name=netbox_hostname, metadata=metadata_xml)
    except Exception as e:
        if "already exists" in str(e):
            logger.info("Service provider already registered")
        else:
            raise
    return saml_helper


@pytest.fixture(scope="module", name="s3_netbox_configuration")
def s3_netbox_configuration_fixture(juju: jubilant.Juju, minio_app: App) -> dict:
    """Return the S3 configuration to use.

    Returns:
        The S3 configuration as a dict
    """
    status = juju.status()
    unit_ip = status.apps[minio_app.name].units[minio_app.name + "/0"].address
    return {
        "endpoint": f"http://{unit_ip}:9000",
        "bucket": "netboxbucket",
        "path": "/",
        "region": "us-east-1",
        "s3-uri-style": "path",
    }


@pytest.fixture(scope="module", name="s3_netbox_credentials")
def s3_netbox_credentials_fixture() -> dict:
    """Return the S3 AWS credentials to use.

    Returns:
        The S3 credentials as a dict
    """
    return {"access-key": "test-access-key", "secret-key": "test-secret-key"}


@pytest.fixture(scope="session")
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju, None, None]:
    """Pytest fixture that wraps :meth:`jubilant.with_model`."""

    def show_debug_log(juju: jubilant.Juju):
        """Show the juju debug log after the tests.

        Args:
            juju: The Juju instance to get the log from.
        """
        if request.session.testsfailed:
            log = juju.debug_log(limit=1000)
            print(log, end="")

    use_existing = request.config.getoption("--use-existing", default=False)
    if use_existing:
        juju = jubilant.Juju()
        yield juju
        show_debug_log(juju)
        return

    model = request.config.getoption("--model")
    if model:
        juju = jubilant.Juju(model=model)
        yield juju
        show_debug_log(juju)
        return

    keep_models = cast(bool, request.config.getoption("--keep-models"))
    with jubilant.temp_model(keep=keep_models) as juju:
        juju.wait_timeout = 10 * 60
        yield juju
        show_debug_log(juju)
        return


@pytest.fixture(scope="module", name="minio_app_name")
def minio_app_name_fixture() -> str:
    return "minio"


@pytest.fixture(scope="module", name="minio_app")
def minio_app_fixture(juju: jubilant.Juju, minio_app_name, s3_netbox_credentials):
    """Deploy and set up minio and s3-integrator needed for s3-like storage backend
    in the HA charms.
    """
    if juju.status().apps.get(minio_app_name):
        logger.info(f"{minio_app_name} already deployed")
        return App(minio_app_name)

    config = s3_netbox_credentials
    juju.deploy(
        minio_app_name,
        channel="edge",
        config=config,
        trust=True,
    )

    juju.wait(lambda status: status.apps[minio_app_name].is_active, timeout=60 * 30)
    return App(minio_app_name)


@pytest.fixture(scope="module", name="nginx_app")
def nginx_app_fixture(
    juju: jubilant.Juju,
    nginx_app_name: str,
) -> App:
    """Deploy nginx."""
    if juju.status().apps.get(nginx_app_name):
        logger.info(f"{nginx_app_name} already deployed")
        return App(nginx_app_name)

    juju.deploy(nginx_app_name, channel="latest/edge", revision=99, trust=True)
    return App(nginx_app_name)


@pytest.fixture(scope="module", name="netbox_nginx_integration")
def netbox_nginx_integration_fixture(
    juju: jubilant.Juju,
    nginx_app: App,
    netbox_app: App,
    netbox_hostname: str,
):
    """Integrate Netbox and Nginx for ingress integration."""
    juju.config(
        nginx_app.name,
        {"service-hostname": netbox_hostname, "path-routes": "/"},
    )
    try:
        juju.integrate(
            netbox_app.name,
            nginx_app.name,
        )
    except jubilant.CLIError as e:
        if "already exists" in str(e):
            logger.info("Relation already exists")
        else:
            raise
    juju.wait(
        jubilant.all_active,
        timeout=15 * 60,
    )
    yield netbox_app
    juju.remove_relation(
        f"{netbox_app.name}:ingress",
        f"{nginx_app.name}:ingress",
    )


@pytest.fixture(scope="module", name="s3_integrator_app")
def s3_integrator_app_fixture(
    juju: jubilant.Juju,
    minio_app: App,
    s3_integrator_app_name: str,
    s3_netbox_configuration: dict,
    s3_netbox_credentials: dict,
) -> App:
    if juju.status().apps.get(s3_integrator_app_name):
        logger.info(f"{s3_integrator_app_name} already deployed")
        return App(s3_integrator_app_name)
    juju.deploy(
        s3_integrator_app_name,
        channel="edge",
    )
    juju.wait(
        lambda status: jubilant.all_blocked(status, s3_integrator_app_name),
        timeout=120,
    )
    status = juju.status()
    minio_addr = status.apps[minio_app.name].units[minio_app.name + "/0"].address

    mc_client = Minio(
        f"{minio_addr}:9000",
        access_key=s3_netbox_credentials["access-key"],
        secret_key=s3_netbox_credentials["secret-key"],
        secure=False,
    )

    # create tempo bucket
    bucket_name = s3_netbox_configuration["bucket"]
    found = mc_client.bucket_exists(bucket_name)
    if not found:
        mc_client.make_bucket(bucket_name)

    # configure s3-integrator
    juju.config(
        "s3-integrator",
        s3_netbox_configuration,
    )

    task = juju.run(f"{s3_integrator_app_name}/0", "sync-s3-credentials", s3_netbox_credentials)
    assert task.status == "completed"
    return App(s3_integrator_app_name)


@pytest.fixture(scope="module", name="postgresql_app")
def postgresql_app_fixture(
    juju: jubilant.Juju,
    postgresql_app_name: str,
):
    """Deploy and set up postgresql charm needed for the 12-factor charm."""
    if juju.status().apps.get(postgresql_app_name):
        logger.info(f"{postgresql_app_name} already deployed")
        return App(postgresql_app_name)

    juju.deploy(
        postgresql_app_name,
        channel="14/stable",
        base="ubuntu@22.04",
        trust=True,
    )
    return App(postgresql_app_name)


@pytest.fixture(scope="module", name="redis_app")
def redis_app_fixture(
    juju: jubilant.Juju,
    redis_app_name: str,
):
    """Deploy and set up postgresql charm needed for the 12-factor charm."""
    if juju.status().apps.get(redis_app_name):
        logger.info(f"{redis_app_name} already deployed")
        return App(redis_app_name)

    juju.deploy(
        redis_app_name,
        channel="edge",
    )
    return App(redis_app_name)


@pytest.fixture(scope="module", name="netbox_app")
def netbox_app_fixture(
    juju: jubilant.Juju,
    netbox_charm: str,
    netbox_app_image: str,
    netbox_app_name: str,
    redis_app: App,
    postgresql_app: App,
    s3_integrator_app: App,
    # netbox_nginx_integration: App,
) -> App:
    """Deploy netbox app."""
    status = juju.status()
    if netbox_app_name in status.apps:
        return App(netbox_app_name)

    resources = {
        "django-app-image": netbox_app_image,
    }
    juju.deploy(
        f"./{netbox_charm}",
        resources=resources,
        config={
            "django-debug": False,
            "django-allowed-hosts": "*",
        },
    )
    juju.integrate(
        f"{netbox_app_name}:s3",
        f"{s3_integrator_app.name}",
    )
    juju.integrate(
        f"{netbox_app_name}:postgresql",
        f"{postgresql_app.name}",
    )
    juju.integrate(
        f"{netbox_app_name}:redis",
        f"{redis_app.name}",
    )
    juju.wait(
        lambda status: jubilant.all_active(
            status, s3_integrator_app.name, postgresql_app.name, redis_app.name, netbox_app_name
        ),
        timeout=15 * 60,
    )

    return App(netbox_app_name)
