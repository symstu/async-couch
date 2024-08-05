import pytest
from async_couch import CouchClient

pytestmark = pytest.mark.anyio

db_name = "test_document_attachment_endpoint"
doc_name = "test_attachment_doc"
attachment_name = "test_attachment"
attachment_content = b"test_text"


@pytest.fixture(scope="session", autouse=True)
async def document(client: CouchClient):
    response = await client.db_create(db_name)
    assert response.status_code == 201

    response = await client.doc_create_or_update(db_name, doc_name, dict(test=True))
    assert response.status_code == 201

    yield response.model.rev

    response = await client.db_delete(db_name)
    assert response.status_code == 200


async def test_create(client: CouchClient, document: str):
    response = await client.attachment_upload(
        db_name,
        doc_name,
        attachment_name,
        "text/plain",
        attachment_content,
        document,
    )
    assert response.status_code == 201

    response = await client.attachment_upload(
        db_name,
        doc_name,
        "%invalid_name#",
        "text/plain",
        attachment_content,
        "%invalid_name#",
    )
    assert response.status_code == 400

    response = await client.attachment_upload(
        "non_existing_db",
        doc_name,
        attachment_name,
        "text/plain",
        attachment_content,
        document,
    )
    assert response.status_code == 404

    response = await client.attachment_upload(
        db_name,
        doc_name,
        attachment_name,
        "text/plain",
        attachment_content,
        "invalid_rev",
    )
    assert response.status_code == 400


async def test_exists(
    client: CouchClient,
):
    response = await client.attachment_exists(db_name, doc_name, attachment_name)
    assert response.status_code == 200

    response = await client.attachment_exists(
        db_name, doc_name, "non_existing_attachment"
    )
    assert response.status_code == 404


async def test_get(
    client: CouchClient,
):
    response = await client.attachment_get(db_name, doc_name, attachment_name)
    assert response.status_code == 200
    assert response.data == attachment_content

    response = await client.attachment_get(db_name, doc_name, "non_existing_attachment")
    assert response.status_code == 404


async def test_delete(
    client: CouchClient,
):
    response = await client.attachment_delete(
        db_name, doc_name, attachment_name, rev="non_existing_rev"
    )
    assert response.status_code == 400

    response = await client.attachment_delete(
        db_name, doc_name, "non_existing_attachment"
    )
    assert response.status_code == 404

    response = await client.attachment_delete(db_name, doc_name, "%invalid_attachment#")
    assert response.status_code == 400

    response = await client.attachment_delete(db_name, doc_name, attachment_name)
    assert response.status_code == 409
