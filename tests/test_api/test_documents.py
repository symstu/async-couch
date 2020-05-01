import pytest

from typing import Callable

from async_couch import CouchClient, exc
from async_couch.utils.content_types import MultipartRelatedAttachment


db_name = 'test_document_endpoint'
doc_name = 'test_doc'
doc_with_attachments = 'test_doc_att'


@pytest.fixture(autouse=True, scope='session')
def database(client: CouchClient, async_run: Callable):
    response = async_run(client.db_create(db_name))
    assert response.status_code == 201

    yield

    response = async_run(client.db_delete(db_name))
    assert response.status_code == 200


def test_create(client: CouchClient, async_run: Callable):
    response = async_run(client.doc_create_or_update(
        db_name, doc_name, dict(val=1)
    ))
    assert response.status_code == 201
    assert response.model.id == doc_name
    assert response.model.rev is not None

    response = async_run(client.doc_create_or_update(
        db_name, doc_name, dict(val=2), rev=response.model.rev
    ))
    assert response.status_code == 201
    assert response.model.ok is True

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_create_or_update(
            db_name, doc_name, dict(val=2), rev='2342&###&&&(**88'
        ))
        assert error.code == 400

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_create_or_update(
            db_name, doc_name, dict(val=2), rev='non_existing_revision'
        ))
        assert error.code == 404

    response = async_run(client.doc_create_or_update(
        db_name, doc_name, dict(val=2), rev=response.model.rev, batch='ok'
    ))
    assert response.status_code == 202
    assert response.model.ok is True


def test_create_with_attachments(client: CouchClient, async_run: Callable):
    attachments = MultipartRelatedAttachment(
        name=b'text', data=b'test_text', mime_type=b'text/plain')
    response = async_run(client.doc_create_or_update(
        db_name, doc_with_attachments, dict(val=-1), attachments=[attachments]
    ))
    assert response.status_code == 201
    assert response.model.ok is True

    response = async_run(client.doc_get(
        db_name, doc_with_attachments, attachments=True))
    assert response.status_code == 200
    assert response.model._files[1].decode() == attachments.data


def test_exists(client: CouchClient, async_run: Callable):
    response = async_run(client.doc_exists(db_name, doc_name))
    assert response.status_code == 200

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_exists(db_name, 'non_existing_doc'))
        assert error.code == 404


def test_get(client: CouchClient, async_run: Callable):
    response = async_run(client.doc_get(db_name, doc_name,
                                        attachments=True,
                                        att_encoding_info=True,
                                        conflicts=True,
                                        deleted_conflicts=True,
                                        latest=True,
                                        local_seq=True,
                                        meta=True,
                                        revs=True,
                                        revs_info=True))
    assert response.status_code == 200
    assert response.model._id == doc_name
    assert response.model.doc.get('val') == 2

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_get(db_name, 'invalid_%%%_name'))
        assert error.code == 400

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_get(db_name, 'non_existing'))
        assert error.code == 404


def test_copy(client: CouchClient, async_run: Callable):
    original = async_run(client.doc_get(db_name, doc_name))
    assert original.status_code == 200

    response = async_run(client.doc_copy(
        db_name, doc_name, 'test_copy', rev=original.model._rev))
    assert response.model.ok is True
    assert response.status_code == 201

    copied = async_run(client.doc_get(db_name, 'test_copy'))
    assert copied.status_code == 200
    assert copied.model.doc.get('val') == original.model.doc.get('val')
    assert copied.model.doc.get('val') == 2

    response = async_run(client.doc_copy(
        db_name, doc_name, 'test_copy2', batch='ok'))
    assert response.model.ok is True
    # todo: returns 201 rather then 202
    # assert response.status_code == 202

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_copy(
            db_name, 'non_existing', 'test_new_copy'))
        assert error.code == 404


def test_delete(client: CouchClient, async_run: Callable):
    doc = async_run(client.doc_get(db_name, doc_name))
    assert doc.status_code == 200

    response = async_run(client.doc_delete(db_name, doc_name, doc.model._rev))
    assert response.status_code == 200
    assert response.model.ok is True

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.doc_delete(db_name, doc_name, doc.model._rev))
        assert error.code == 404
