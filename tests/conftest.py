import asyncio
import os

import pytest
import typing
from testcontainers.core.container import DockerContainer
from async_couch import get_couch_client, CouchClient
from dotenv import load_dotenv
from testcontainers.core.waiting_utils import wait_for_logs

load_dotenv()


@pytest.fixture(scope="session")
def loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def async_run(loop: asyncio.AbstractEventLoop) -> typing.Callable:
    return loop.run_until_complete


@pytest.fixture(scope="session")
def client() -> CouchClient:
    user = os.getenv("COUCHDB_USER")
    password = os.getenv("COUCHDB_PASSWORD")
    return get_couch_client(user=user, password=password)

#
# @pytest.fixture(scope="session", autouse=True)
# def docker_couch_server():
#     with DockerContainer(
#         "couchdb",
#     ) as database:
#         database.with_env(
#             "COUCHDB_USER",
#             os.environ["COUCHDB_USER"],
#         )
#         database.with_env(
#             "COUCHDB_PASSWORD",
#             os.environ["COUCHDB_PASSWORD"],
#         )
#         database.with_exposed_ports(5984)
#         database.with_volume_mapping("./.data", "/opt/couchdb/data")
#         wait_for_logs(database, "Apache CouchDB has started")
#         yield database
