import pytest
from async_couch import CouchClient
from async_couch.utils.content_types import MultipartRelatedAttachment


pytestmark = pytest.mark.anyio

db_name = "test_document_endpoint"
doc_name = "test_doc"
doc_with_attachments = "test_doc_att"


@pytest.fixture(scope="session")
async def database(client: CouchClient):
    response = await client.db_create(db_name)
    assert response.status_code == 201

    yield response

    response = await client.db_delete(db_name)
    assert response.status_code == 200


async def test_create(client: CouchClient, database):
    response = await client.doc_create_or_update(db_name, doc_name, dict(val=1))
    assert response.status_code == 201
    assert response.model.id == doc_name
    assert response.model.rev is not None

    response = await client.doc_create_or_update(
        db_name, doc_name, dict(val=2), rev=response.model.rev
    )
    assert response.status_code == 201
    assert response.model.ok is True
    _rev = response.model.rev

    response = await client.doc_create_or_update(
        db_name, doc_name, dict(val=2), rev="2342&###&&&(**88"
    )
    assert response.status_code == 400

    response = await client.doc_create_or_update(
        db_name, doc_name, dict(val=2), rev="non_existing_revision"
    )
    assert response.status_code == 400

    response = await client.doc_create_or_update(
        db_name, doc_name, dict(val=2), rev=_rev, batch="ok"
    )
    assert response.status_code == 202
    assert response.model.ok is True


async def test_create_with_attachments(client: CouchClient, database):
    attachments = MultipartRelatedAttachment(
        name=b"text", data=b"test_text", mime_type=b"text/plain"
    )
    response = await client.doc_create_or_update(
        db_name, doc_with_attachments, dict(val=-1), attachments=[attachments]
    )
    assert response.status_code == 201
    assert response.model.ok is True

    response = await client.doc_get(db_name, doc_with_attachments, attachments=True)
    assert response.status_code == 200
    assert response.model._files[1].decode() == attachments.data


async def test_exists(client: CouchClient, database):
    response = await client.doc_exists(db_name, doc_name)
    assert response.status_code == 200

    response = await client.doc_exists(db_name, "non_existing_doc")
    assert response.status_code == 404


async def test_get(client: CouchClient, database):
    response = await client.doc_get(
        db_name,
        doc_name,
        attachments=True,
        att_encoding_info=True,
        conflicts=True,
        deleted_conflicts=True,
        latest=True,
        local_seq=True,
        meta=True,
        revs=True,
        revs_info=True,
    )
    assert response.status_code == 200
    assert response.model._id == doc_name
    assert response.model.doc.get("val") == 2

    response = await client.doc_get(db_name, "invalid_%%%_name")
    assert response.status_code == 400

    response = await client.doc_get(db_name, "non_existing")
    assert response.status_code == 404


async def test_copy(client: CouchClient, database):
    original = await client.doc_get(db_name, doc_name)
    assert original.status_code == 200

    response = await client.doc_copy(
        db_name, doc_name, "test_copy", rev=original.model._rev
    )
    assert response.model.ok is True
    assert response.status_code == 201

    copied = await client.doc_get(db_name, "test_copy")
    assert copied.status_code == 200
    assert copied.model.doc.get("val") == original.model.doc.get("val")
    assert copied.model.doc.get("val") == 2

    response = await client.doc_copy(db_name, doc_name, "test_copy2", batch="ok")
    assert response.model.ok is True
    # todo: returns 201 rather then 202
    # assert response.status_code == 202

    response = await client.doc_copy(db_name, "non_existing", "test_new_copy")
    assert response.status_code == 404


async def test_delete(client: CouchClient, database):
    doc = await client.doc_get(db_name, doc_name)
    assert doc.status_code == 200

    response = await client.doc_delete(db_name, doc_name, doc.model._rev)
    assert response.status_code == 200
    assert response.model.ok is True

    response = await client.doc_delete(db_name, doc_name, doc.model._rev)
    assert response.status_code == 404
