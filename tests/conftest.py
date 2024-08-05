import os

import pytest
from async_couch import get_couch_client, CouchClient
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
        pytest.param(("asyncio", {"use_uvloop": False}), id="asyncio"),
        pytest.param(
            ("trio", {"restrict_keyboard_interrupt_to_checkpoints": True}), id="trio"
        ),
    ],
    scope="session",
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
async def cleanup(client):
    await client.db_delete("test_db_01")
    await client.db_delete("test_document_endpoint")
    await client.db_delete("test_document_attachment_endpoint")
    await client.db_delete("test_design_document_endpoint")
    yield


@pytest.fixture(scope="session")
def client(anyio_backend) -> CouchClient:
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
