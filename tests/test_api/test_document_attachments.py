import pytest

from typing import Callable

from async_couch import CouchClient, exc


db_name = 'test_document_attachment_endpoint'
doc_name = 'test_attachment_doc'
attachment_name = 'test_attachment'
attachment_content = b'test_text'


@pytest.fixture(autouse=True, scope='session')
def document(client: CouchClient, async_run: Callable):
    response = async_run(client.db_create(db_name))
    assert response.status_code == 201

    response = async_run(client.doc_create_or_update(
        db_name, doc_name, dict(test=True)))
    assert response.status_code == 201

    yield response.model.rev

    response = async_run(client.db_delete(db_name))
    assert response.status_code == 200


def test_create(client: CouchClient, async_run: Callable, document: str):
    response = async_run(client.attachment_upload(
        db_name, doc_name, attachment_name, 'text/plain', attachment_content,
        document
    ))
    assert response.status_code == 201

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_upload(
            db_name, doc_name, '%invalid_name#', 'text/plain',
            attachment_content, '%invalid_name#'
        ))
        assert error.code == 400

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_upload(
            'non_existing_db', doc_name, attachment_name, 'text/plain',
            attachment_content, document
        ))
        assert error.code == 404

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_upload(
            db_name, doc_name, attachment_name, 'text/plain',
            attachment_content, 'invalid_rev'
        ))
        assert error == 409


def test_exists(client: CouchClient, async_run: Callable):
    response = async_run(client.attachment_exists(
        db_name, doc_name, attachment_name
    ))
    assert response.status_code == 200

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_exists(
            db_name, doc_name, 'non_existing_attachment'
        ))
        assert error.code == 404


def test_get(client: CouchClient, async_run: Callable):
    response = async_run(client.attachment_get(
        db_name, doc_name, attachment_name
    ))
    assert response.status_code == 200
    assert response.data == attachment_content

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_get(
            db_name, doc_name, 'non_existing_attachment'
        ))
        assert error == 404


def test_delete(client: CouchClient, async_run: Callable):
    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_delete(
            db_name, doc_name, attachment_name, rev='non_existing_rev'
        ))
        assert error.code == 409

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_delete(
            db_name, doc_name, 'non_existing_attachment'
        ))
        assert error.code == 404

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_delete(
            db_name, doc_name, '%invalid_attachment#'
        ))
        assert error.code == 400

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.attachment_delete(
            db_name, doc_name, attachment_name
        ))
        assert error.code == 400
