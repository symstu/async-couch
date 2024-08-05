import pytest

from async_couch import CouchClient

pytestmark = pytest.mark.anyio

db_name = "test_design_document_endpoint"
design_name = "test_design_doc"
design_body = {"views": {"test_view": {"map": "function (doc) { emit(1, 1) }"}}}


@pytest.fixture(scope="session", autouse=True)
async def prepare_all(client: CouchClient):
    response = await client.db_create(db_name)
    assert response.status_code == 201

    response = await client.doc_create_or_update(
        db_name, f"_design/{design_name}", design_body
    )
    assert response.status_code == 201

    yield

    response = await client.db_delete(db_name)
    assert response.status_code == 200


async def test_design_info(client: CouchClient):
    result = await client.des_info(db_name, design_name)

    assert result.status_code == 200
    assert result.model.name == "test_design_doc"
    assert result.model.view_index.get("language") == "javascript"


async def test_view_exec(client: CouchClient):
    result = await client.view_exec(db_name, design_name, "test_view")

    assert result.status_code == 200
    assert result.model.total_rows == 0
