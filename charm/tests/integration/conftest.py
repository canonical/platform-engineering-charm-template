# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the NetBox charm integration tests."""

import logging
import os.path
import typing
from secrets import token_hex

import boto3
import pytest
import pytest_asyncio
from botocore.config import Config as BotoConfig
from juju.application import Application
from juju.model import Model
from pytest import Config
from pytest_operator.plugin import OpsTest
from saml_test_helper import SamlK8sTestHelper

from tests.conftest import NETBOX_IMAGE_PARAM

logger = logging.getLogger(__name__)

# caused by pytest fixtures, mark does not work in fixtures
# pylint: disable=too-many-arguments, unused-argument


@pytest_asyncio.fixture(scope="module", name="model")
async def model_fixture(ops_test: OpsTest) -> Model:
    """Return the current testing juju model."""
    assert ops_test.model
    return ops_test.model


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


@pytest_asyncio.fixture(scope="module", name="nginx_app")
async def nginx_app_fixture(
    ops_test: OpsTest,
    nginx_app_name: str,
    model: Model,
    pytestconfig: Config,
) -> Application:
    """Deploy nginx."""
    async with ops_test.fast_forward():
        app = await model.deploy(nginx_app_name, channel="latest/edge", revision=99, trust=True)
        await model.wait_for_idle()
    return app


@pytest_asyncio.fixture(scope="module", name="saml_app")
async def saml_app_fixture(
    ops_test: OpsTest,
    saml_app_name: str,
    model: Model,
    pytestconfig: Config,
) -> Application:
    """Deploy saml."""
    async with ops_test.fast_forward():
        app = await model.deploy(saml_app_name, channel="latest/edge")
        await model.wait_for_idle()
    return app


@pytest_asyncio.fixture(scope="module", name="postgresql_app")
async def postgresql_app_fixture(
    ops_test: OpsTest,
    postgresql_app_name: str,
    model: Model,
    pytestconfig: Config,
) -> Application:
    """Deploy postgresql."""
    if postgresql_app_name in model.applications:
        return model.applications[postgresql_app_name]
    async with ops_test.fast_forward():
        app = await model.deploy(postgresql_app_name, channel="14/stable", trust=True)
        await model.wait_for_idle(apps=[postgresql_app_name], status="active")
    return app


@pytest.fixture(scope="module", name="s3_netbox_configuration")
def s3_netbox_configuration_fixture(minio_app_name: str) -> dict:
    """Return the S3 configuration to use.

    Returns:
        The S3 configuration as a dict
    """
    return {
        "endpoint": f"http://{minio_app_name}-0.{minio_app_name}-endpoints:9000",
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
    return {
        "access-key": token_hex(16),
        "secret-key": token_hex(16),
    }


# @pytest_asyncio.fixture(scope="module", name="s3_integrator_app")
# async def s3_integrator_app_fixture(
#     model: Model,
#     s3_integrator_app_name: str,
#     s3_netbox_configuration: dict,
#     s3_netbox_credentials: dict,
# ):
#     """Returns a s3-integrator app configured with parameters."""
#     if "s3-integrator" in model.applications:
#         return model.applications["s3-integrator"]

#     s3_integrator_app = await model.deploy(
#         "s3-integrator",
#         application_name=s3_integrator_app_name,
#         channel="1/stable",
#         config=s3_netbox_configuration,
#     )
#     await model.wait_for_idle(apps=[s3_integrator_app_name], idle_period=5, status="blocked")
#     action_sync_s3_credentials: Action = await s3_integrator_app.units[0].run_action(
#         "sync-s3-credentials",
#         **s3_netbox_credentials,
#     )
#     await action_sync_s3_credentials.wait()
#     await model.wait_for_idle(apps=[s3_integrator_app_name], status="active")
#     return s3_integrator_app


@pytest_asyncio.fixture(scope="module", name="netbox_app_image")
def netbox_app_image_fixture(pytestconfig: Config) -> str:
    """Get value from parameter netbox-image."""
    netbox_app_image = pytestconfig.getoption(NETBOX_IMAGE_PARAM)
    assert netbox_app_image, f"{NETBOX_IMAGE_PARAM} must be set"
    return netbox_app_image


@pytest_asyncio.fixture(scope="module", name="netbox_charm")
async def netbox_charm_fixture(pytestconfig: Config) -> str:
    """Get value from parameter charm-file."""
    charm = pytestconfig.getoption("--charm-file")
    assert charm, "--charm-file must be set"
    if not os.path.exists(charm):
        logger.info("Using parent directory for charm file")
        charm = os.path.join("..", charm)
    return charm


# @pytest_asyncio.fixture(scope="module", name="netbox_app")
# async def netbox_app_fixture(
#     ops_test: OpsTest,
#     model: Model,
#     netbox_charm: str,
#     netbox_app_image: str,
#     netbox_app_name: str,
#     postgresql_app_name: str,
#     redis_app_name: str,
#     redis_app: Application,
#     postgresql_app: Application,
#     pytestconfig: Config,
#     s3_netbox_configuration: dict,
#     s3_integrator_app_name: str,
#     s3_integrator_app: Application,
# ) -> Application:
#     """Deploy netbox app."""
#     if netbox_app_name in model.applications:
#         return model.applications[netbox_app_name]

#     resources = {
#         "django-app-image": netbox_app_image,
#     }
#     app = await model.deploy(
#         f"./{netbox_charm}",
#         resources=resources,
#         config={
#             "django-debug": False,
#             "django-allowed-hosts": "*",
#         },
#     )
#     # If update_status comes before pebble ready, the unit gets to
#     # error state. Just do not fail in that case.
#     await model.wait_for_idle(apps=[netbox_app_name], raise_on_error=False)

#     await model.relate(f"{netbox_app_name}:s3", f"{s3_integrator_app_name}")
#     await model.relate(f"{netbox_app_name}:postgresql", f"{postgresql_app_name}")
#     await model.relate(f"{netbox_app_name}:redis", f"{redis_app_name}")

#     await model.wait_for_idle(apps=[netbox_app_name, postgresql_app_name], status="active")

#     return app


# @pytest_asyncio.fixture(scope="module", name="redis_app")
# async def redis_app_fixture(
#     redis_app_name: str,
#     model: Model,
#     pytestconfig: Config,
# ) -> Application:
#     """Deploy redis-k8s."""
#     if redis_app_name in model.applications:
#         return model.applications[redis_app_name]

#     app = await model.deploy(redis_app_name, channel="edge")
#     await model.wait_for_idle(apps=[redis_app_name], status="active")
#     return app


@pytest_asyncio.fixture(scope="module", name="netbox_nginx_integration")
async def netbox_nginx_integration_fixture(
    model: Model,
    nginx_app: Application,
    netbox_app: Application,
    netbox_hostname: str,
):
    """Integrate Netbox and Nginx for ingress integration."""
    await nginx_app.set_config({"service-hostname": netbox_hostname, "path-routes": "/"})
    await model.wait_for_idle()
    relation = await model.add_relation(f"{netbox_app.name}", f"{nginx_app.name}")
    await model.wait_for_idle(
        apps=[netbox_app.name, nginx_app.name], idle_period=30, status="active"
    )
    self_signed_cerfiticates = await model.deploy(
        "self-signed-certificates", channel="latest/edge", trust=True
    )
    await model.relate(f"{nginx_app.name}", f"{self_signed_cerfiticates.name}")
    await model.wait_for_idle()
    yield relation
    await netbox_app.destroy_relation("ingress", f"{nginx_app.name}:ingress")
    await model.remove_application(self_signed_cerfiticates.name)


@pytest_asyncio.fixture(scope="module", name="saml_helper")
async def saml_helper_fixture(
    model: Model,
) -> SamlK8sTestHelper:
    """Fixture for SamlHelper."""
    saml_helper = SamlK8sTestHelper.deploy_saml_idp(model.name)
    return saml_helper


@pytest_asyncio.fixture(scope="module", name="netbox_saml_integration")
async def netbox_saml_integration_fixture(
    model: Model,
    saml_app: Application,
    netbox_app: Application,
    netbox_hostname: str,
    saml_helper: SamlK8sTestHelper,
):
    """Integrate Netbox and SAML for saml integration."""
    await netbox_app.set_config(
        {
            "saml-sp-entity-id": f"https://{netbox_hostname}",
            # The saml Name for FriendlyName "uid"
            "saml-username": "urn:oid:0.9.2342.19200300.100.1.1",
        }
    )
    saml_helper.prepare_pod(model.name, f"{saml_app.name}-0")
    saml_helper.prepare_pod(model.name, f"{netbox_app.name}-0")
    await saml_app.set_config(
        {
            "entity_id": f"https://{saml_helper.SAML_HOST}/metadata",
            "metadata_url": f"https://{saml_helper.SAML_HOST}/metadata",
        }
    )
    await model.wait_for_idle(idle_period=30)
    relation = await model.add_relation(saml_app.name, netbox_app.name)
    await model.wait_for_idle(
        apps=[saml_app.name, netbox_app.name],
        idle_period=30,
        status="active",
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
    saml_helper.register_service_provider(name=netbox_hostname, metadata=metadata_xml)
    yield relation
    await netbox_app.destroy_relation("saml", f"{saml_app.name}:saml")


# @pytest.fixture(scope="module", name="localstack_address")
# def localstack_address_fixture(pytestconfig: Config):
#     """Provides localstack IP address to be used in the integration test."""
#     address = pytestconfig.getoption("--localstack-address")
#     if not address:
#         raise ValueError("--localstack-address argument is required for selected test cases")
#     yield address


@pytest.fixture(scope="function", name="boto_s3_client")
def boto_s3_client_fixture(s3_netbox_configuration: dict, s3_netbox_credentials: dict):
    """Return a S3 boto3 client ready to use

    Returns:
        The boto S3 client
    """
    s3_client_config = BotoConfig(
        region_name=s3_netbox_configuration["region"],
        s3={
            "addressing_style": "virtual",
        },
        # no_proxy env variable is not read by boto3, so
        # this is needed for the tests to avoid hitting the proxy.
        proxies={},
    )

    s3_client = boto3.client(
        "s3",
        s3_netbox_configuration["region"],
        aws_access_key_id=s3_netbox_credentials["access-key"],
        aws_secret_access_key=s3_netbox_credentials["secret-key"],
        endpoint_url=s3_netbox_configuration["endpoint"],
        use_ssl=False,
        config=s3_client_config,
    )
    yield s3_client


@pytest.fixture(scope="function", name="s3_netbox_bucket")
def s3_netbox_bucket_fixture(
    s3_netbox_configuration: dict, s3_netbox_credentials: dict, boto_s3_client: typing.Any
):
    """Creates a bucket using S3 configuration."""
    bucket_name = s3_netbox_configuration["bucket"]
    boto_s3_client.create_bucket(Bucket=bucket_name)
    yield
    objectsresponse = boto_s3_client.list_objects(Bucket=bucket_name)
    if "Contents" in objectsresponse:
        for c in objectsresponse["Contents"]:
            boto_s3_client.delete_object(Bucket=bucket_name, Key=c["Key"])
    boto_s3_client.delete_bucket(Bucket=bucket_name)


from collections.abc import Generator
from typing import cast

#--------------------------------------------------
import jubilant
from minio import Minio

from charm.tests.integration.types import App


@pytest.fixture(scope="session")
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju, None, None]:
    """Pytest fixture that wraps :meth:`jubilant.with_model`."""

    def show_debug_log(juju: jubilant.Juju):
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
    """Deploy and set up minio and s3-integrator needed for s3-like storage backend in the HA charms."""

    if juju.status().apps.get(minio_app_name):
        logger.info(f"{minio_app_name} already deployed")
        return

    config = s3_netbox_credentials
    juju.deploy(
        minio_app_name,
        channel="edge",
        config=config,
        trust=True,
    )

    juju.wait(lambda status: status.apps[minio_app_name].is_active, timeout=60 * 30)
    return App(minio_app_name)

@pytest.fixture(scope="module", name="s3_integrator_app")
def s3_integrator_app_fixture(
    juju: jubilant.Juju,
    minio_app: App, 
    s3_netbox_configuration: dict,
    s3_netbox_credentials: dict,):
    s3_integrator = "s3-integrator"
    if juju.status().apps.get(s3_integrator):
        logger.info(f"{s3_integrator} already deployed")
        return App(s3_integrator)

    juju.deploy(
        s3_integrator,
        channel="edge",
    )
    juju.wait(
        lambda status: jubilant.all_blocked(status, s3_integrator),
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

    task = juju.run(f"{s3_integrator}/0", "sync-s3-credentials", s3_netbox_credentials)
    assert task.status == "completed"
    return App(s3_integrator)


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
        lambda status: jubilant.all_active(status, s3_integrator_app.name,postgresql_app.name, redis_app.name, netbox_app_name),
        timeout=300,
    )

    return App(netbox_app_name)
    return App(netbox_app_name)
    return App(netbox_app_name)
