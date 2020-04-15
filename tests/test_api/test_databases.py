import pytest

from typing import Callable

from async_couch import CouchClient, exc


db_name = 'test_db_01'
invalid_db_name = 'invalid_%^^&_name'
non_existing_db = 'non_existing_database'


def test_create(async_run: Callable, client: CouchClient):
    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_create(invalid_db_name))
        assert error.code == 400

    response = async_run(client.db_create(db_name))
    assert response.status_code == 201
    assert response.json().get('ok') is True

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_create(db_name))
        assert error.code == 412


def test_existing(async_run: Callable, client: CouchClient):
    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_exists(non_existing_db))
        assert error.code == 404

    response = async_run(client.db_exists(db_name))
    assert response.status_code == 200


def test_create_doc(async_run: Callable, client: CouchClient):
    doc = dict(test=True)

    response = async_run(client.db_crete_doc(db_name, doc))
    assert response.status_code == 201

    response = async_run(client.db_crete_doc(db_name, doc, batch='ok'))
    assert response.status_code == 202

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_crete_doc(invalid_db_name, doc))
        assert error.status_code == 400

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_crete_doc(non_existing_db, doc))
        assert error.status_code == 404


def test_delete(async_run: Callable, client: CouchClient):
    response = async_run(client.db_delete(db_name))
    assert response.status_code == 200

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_delete(invalid_db_name))
        assert error.code == 400

    with pytest.raises(exc.CouchResponseError) as error:
        async_run(client.db_delete(non_existing_db))
        assert error.code == 404
