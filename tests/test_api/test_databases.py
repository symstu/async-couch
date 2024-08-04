from typing import Callable

from async_couch import CouchClient


db_name = "test_db_01"
invalid_db_name = "invalid_%^^&_name"
non_existing_db = "non_existing_database"
doc_id = None


def test_create(async_run: Callable, client: CouchClient):
    response = async_run(client.db_create(invalid_db_name))
    assert response.status_code == 400

    response = async_run(client.db_create(db_name))
    assert response.status_code == 201
    assert response.json().get("ok") is True

    response = async_run(client.db_create(db_name))
    assert response.status_code == 412


def test_existing(async_run: Callable, client: CouchClient):
    response = async_run(client.db_exists(non_existing_db))
    assert response.status_code == 404

    response = async_run(client.db_exists(db_name))
    assert response.status_code == 200


def test_create_doc(async_run: Callable, client: CouchClient):
    global doc_id
    doc = dict(test=True)

    response = async_run(client.db_create_doc(db_name, doc))
    assert response.status_code == 201

    doc_id = response.model.id

    response = async_run(client.db_create_doc(db_name, doc, batch="ok"))
    assert response.status_code == 202

    response = async_run(client.db_create_doc(non_existing_db, doc))
    assert response.status_code == 404


def test_all_docs(async_run: Callable, client: CouchClient):
    response = async_run(client.db_all_docs(db_name, keys=[doc_id]))
    assert response.status_code == 200
    assert len(response.model.rows) == 1


def test_design_docs(async_run: Callable, client: CouchClient):
    response = async_run(client.db_design_docs(db_name, keys=[doc_id]))
    assert response.status_code == 200
    assert len(response.model.rows) == 1


def test_delete(async_run: Callable, client: CouchClient):
    response = async_run(client.db_delete(db_name))
    assert response.status_code == 200

    response = async_run(client.db_delete(invalid_db_name))
    assert response.status_code == 404

    response = async_run(client.db_delete(non_existing_db))
    assert response.status_code == 404
