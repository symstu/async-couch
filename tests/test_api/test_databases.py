import pytest

from async_couch import CouchClient

pytestmark = pytest.mark.anyio

db_name = "test_db_01"
invalid_db_name = "invalid_%^^&_name"
non_existing_db = "non_existing_database"
doc_id = None


async def test_create(client: CouchClient):
    response = await client.db_create(invalid_db_name)
    assert response.status_code == 400

    response = await client.db_create(db_name)
    assert response.status_code == 201
    assert response.json().get("ok") is True

    response = await client.db_create(db_name)
    assert response.status_code == 412


async def test_existing(client: CouchClient):
    response = await client.db_exists(non_existing_db)
    assert response.status_code == 404

    response = await client.db_exists(db_name)
    assert response.status_code == 200


async def test_create_doc(client: CouchClient):
    global doc_id
    doc = dict(test=True)

    response = await client.db_create_doc(db_name, doc)
    assert response.status_code == 201

    doc_id = response.model.id

    response = await client.db_create_doc(db_name, doc, batch="ok")
    assert response.status_code == 202

    response = await client.db_create_doc(non_existing_db, doc)
    assert response.status_code == 404


async def test_all_docs(client: CouchClient):
    response = await client.db_all_docs(db_name, keys=[doc_id])
    assert response.status_code == 200
    assert len(response.model.rows) == 1


async def test_design_docs(client: CouchClient):
    response = await client.db_design_docs(db_name, keys=[doc_id])
    assert response.status_code == 200
    assert len(response.model.rows) == 1


async def test_delete(client: CouchClient):
    response = await client.db_delete(db_name)
    assert response.status_code == 200

    response = await client.db_delete(invalid_db_name)
    assert response.status_code == 404

    response = await client.db_delete(non_existing_db)
    assert response.status_code == 404
