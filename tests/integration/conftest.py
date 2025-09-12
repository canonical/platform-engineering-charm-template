# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the NetBox charm integration tests."""

import logging
import os.path
import subprocess
from collections.abc import Generator
from typing import cast

import jubilant
import kubernetes
import pytest
import requests
from minio import Minio
from pytest import Config
from requests import HTTPError
from requests.adapters import HTTPAdapter
from saml_test_helper import SamlK8sTestHelper
from urllib3.util.retry import Retry

from tests.conftest import NETBOX_IMAGE_PARAM
from tests.integration.types import App

logger = logging.getLogger(__name__)

# pylint things `juju`` is redefined, but it's a fixture
# pylint: disable=redefined-outer-name

MINIO_APP_NAME = "minio"
NETBOX_APP_NAME = "netbox-k8s"
NGINX_APP_NAME = "nginx-ingress-integrator"
POSTGRESQL_APP_NAME = "postgresql-k8s"
REDIS_APP_NAME = "redis-k8s"
SAML_APP_NAME = "saml-integrator"
S3_INTEGRATOR_APP_NAME = "s3-integrator"


@pytest.fixture(scope="module", name="netbox_hostname")
def netbox_hostname_fixture() -> str:
    """Return the name of the NetBox hostname used for tests."""
    return "netbox-k8s.internal"


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
    """Return the SamlK8sTestHelper instance used for tests."""
    model_name = juju.status().model.name
    try:
        saml_helper = SamlK8sTestHelper.deploy_saml_idp(model_name)
    except kubernetes.client.ApiException as e:
        if e.reason == "Conflict" and "already exists" in str(e):
            logger.info("SAML IDP already deployed")
            saml_helper = SamlK8sTestHelper(model_name)
        else:
            raise
    return saml_helper


@pytest.fixture(scope="module", name="saml_app")
def saml_app_fixture(
    juju: jubilant.Juju,
) -> App:
    """Deploy saml."""
    if juju.status().apps.get(SAML_APP_NAME):
        logger.info("%s already deployed", SAML_APP_NAME)
        return App(SAML_APP_NAME)
    juju.deploy(
        SAML_APP_NAME,
        channel="latest/edge",
    )
    return App(SAML_APP_NAME)


@pytest.fixture(scope="module", name="netbox_saml_integration")
def netbox_saml_integration_fixture(
    juju: jubilant.Juju,
    saml_app: App,
    netbox_app: App,
    netbox_hostname: str,
    saml_helper: SamlK8sTestHelper,
):
    """Integrate NetBox and SAML for saml integration."""
    juju.config(
        netbox_app.name,
        {
            "saml-sp-entity-id": f"https://{netbox_hostname}",
            # The saml Name for FriendlyName "uid"
            "saml-username": "urn:oid:0.9.2342.19200300.100.1.1",
        },
    )
    model_name = juju.status().model.name
    saml_helper.prepare_pod(model_name, f"{saml_app.name}-0")
    saml_helper.prepare_pod(model_name, f"{netbox_app.name}-0")

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
    except jubilant.CLIError as e:
        if "already exists" in str(e):
            logger.info("Relation already exists")
        else:
            raise
    juju.wait(
        lambda status: jubilant.all_active(status, saml_app.name, netbox_app.name),
        timeout=10 * 60,
    )

    # For the saml_helper, a SAML XML metadata for the service is needed.
    # There are instructions to generate it in:
    # https://python-social-auth.readthedocs.io/en/latest/backends/saml.html#basic-usage.
    # This one is instead a minimalistic one that works for the test.
    metadata_xml = f"""
    <md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" cacheDuration="P10D"
                         entityID="https://{netbox_hostname}">
      <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
                          AuthnRequestsSigned="false" WantAssertionsSigned="true">
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                     Location="https://{netbox_hostname}/oauth/complete/saml/"
                                     index="1"/>
      </md:SPSSODescriptor>
    </md:EntityDescriptor>
    """
    try:
        saml_helper.register_service_provider(name=netbox_hostname, metadata=metadata_xml)
    except HTTPError as e:
        if "already exists" in str(e):
            logger.info("Service provider already registered")
        else:
            raise
    return saml_helper


@pytest.fixture(scope="module", name="s3_netbox_configuration")
def s3_netbox_configuration_fixture(juju: jubilant.Juju, minio_app: App) -> dict:
    """Return the S3 configuration to use.

    Returns:
        The S3 configuration as a dict.
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
        The S3 credentials as a dict.
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


@pytest.fixture(scope="module", name="minio_app")
def minio_app_fixture(juju: jubilant.Juju, s3_netbox_credentials):
    """Deploy and set up minio and s3-integrator needed for s3-like storage backend."""
    if juju.status().apps.get(MINIO_APP_NAME):
        logger.info("%s already deployed", MINIO_APP_NAME)
        return App(MINIO_APP_NAME)

    juju.deploy(
        MINIO_APP_NAME,
        channel="edge",
        config=s3_netbox_credentials,
        trust=True,
    )

    juju.wait(lambda status: status.apps[MINIO_APP_NAME].is_active, timeout=60 * 30)
    return App(MINIO_APP_NAME)


@pytest.fixture(scope="module", name="nginx_app")
def nginx_app_fixture(
    juju: jubilant.Juju,
) -> App:
    """Deploy nginx."""
    if juju.status().apps.get(NGINX_APP_NAME):
        logger.info("%s already deployed", NGINX_APP_NAME)
        return App(NGINX_APP_NAME)

    juju.deploy(NGINX_APP_NAME, channel="latest/edge", revision=99, trust=True)
    return App(NGINX_APP_NAME)


@pytest.fixture(scope="module", name="netbox_nginx_integration")
def netbox_nginx_integration_fixture(
    juju: jubilant.Juju,
    nginx_app: App,
    netbox_app: App,
    netbox_hostname: str,
):
    """Integrate NetBox and Nginx for ingress integration."""
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
    s3_netbox_configuration: dict,
    s3_netbox_credentials: dict,
) -> App:
    """Deploy and set up s3-integrator"""
    if juju.status().apps.get(S3_INTEGRATOR_APP_NAME):
        logger.info("%s already deployed", S3_INTEGRATOR_APP_NAME)
        return App(S3_INTEGRATOR_APP_NAME)
    juju.deploy(
        S3_INTEGRATOR_APP_NAME,
        channel="edge",
    )
    juju.wait(
        lambda status: jubilant.all_blocked(status, S3_INTEGRATOR_APP_NAME),
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

    task = juju.run(f"{S3_INTEGRATOR_APP_NAME}/0", "sync-s3-credentials", s3_netbox_credentials)
    assert task.status == "completed"
    return App(S3_INTEGRATOR_APP_NAME)


@pytest.fixture(scope="module", name="postgresql_app")
def postgresql_app_fixture(
    juju: jubilant.Juju,
):
    """Deploy and set up postgresql charm needed for the NetBox charm."""
    if juju.status().apps.get(POSTGRESQL_APP_NAME):
        logger.info("%s already deployed", POSTGRESQL_APP_NAME)
        return App(POSTGRESQL_APP_NAME)

    juju.deploy(
        POSTGRESQL_APP_NAME,
        channel="14/stable",
        base="ubuntu@22.04",
        trust=True,
    )
    return App(POSTGRESQL_APP_NAME)


@pytest.fixture(scope="module", name="redis_app")
def redis_app_fixture(
    juju: jubilant.Juju,
):
    """Deploy and set up postgresql charm needed for the NetBox charm."""
    if juju.status().apps.get(REDIS_APP_NAME):
        logger.info("%s already deployed", REDIS_APP_NAME)
        return App(REDIS_APP_NAME)

    juju.deploy(
        REDIS_APP_NAME,
        channel="edge",
    )
    return App(REDIS_APP_NAME)


@pytest.fixture(scope="module", name="netbox_barebones")
def netbox_barebones_fixture(
    juju: jubilant.Juju,
    netbox_charm: str,
    netbox_app_image: str,
) -> App:
    """Deploy NetBox app without any relations."""
    status = juju.status()
    if NETBOX_APP_NAME in status.apps:
        return App(NETBOX_APP_NAME)

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
    return App(NETBOX_APP_NAME)


@pytest.fixture(scope="module", name="netbox_app")
def netbox_app_fixture(
    juju: jubilant.Juju,
    netbox_barebones: App,
    redis_app: App,
    postgresql_app: App,
    s3_integrator_app: App,
) -> App:
    """Deploy NetBox app with necessary integrations."""
    try:
        juju.integrate(
            f"{netbox_barebones.name}:s3",
            f"{s3_integrator_app.name}",
        )
        juju.integrate(
            f"{netbox_barebones.name}:postgresql",
            f"{postgresql_app.name}",
        )
        juju.integrate(
            f"{netbox_barebones.name}:redis",
            f"{redis_app.name}",
        )
    except jubilant.CLIError as e:
        if "already exists" in str(e):
            logger.info("Relation already exists")
        else:
            raise
    juju.wait(
        lambda status: jubilant.all_active(
            status,
            s3_integrator_app.name,
            postgresql_app.name,
            redis_app.name,
            netbox_barebones.name,
        ),
        timeout=15 * 60,
    )

    return App(netbox_barebones.name)


@pytest.fixture(scope="module", name="identity_bundle")
def deploy_identity_bundle_fixture(juju: jubilant.Juju) -> None:
    """Deploy Canonical identity bundle."""
    if juju.status().apps.get("hydra"):
        logger.info("identity-platform is already deployed")
        return
    juju.deploy("identity-platform", channel="latest/edge", trust=True)
    juju.remove_application("kratos-external-idp-integrator")
    juju.config("kratos", {"enforce_mfa": False})


@pytest.fixture(scope="session")
def browser_context_manager() -> None:
    """
    A session-scoped fixture that installs the Playwright browser.
    This ensures the browser is installed only for oauth test.
    """
    try:
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to install Playwright browser: {e.stderr}")


@pytest.fixture(scope="function", name="http")
def fixture_http_client() -> Generator[requests.Session]:
    """Return the --test-flask-image test parameter."""
    retry_strategy = Retry(
        total=5,
        connect=5,
        read=5,
        other=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "POST", "GET", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    with requests.Session() as http:
        http.mount("http://", adapter)
        yield http
