from typing import Callable

import pytest

from async_couch import CouchClient


db_name = 'test_design_document_endpoint'
design_name = 'test_design_doc'
design_body = {
    "views": {
        "test_view": {
            "map": "function (doc) { emit(1, 1) }"
        }
    }
}


@pytest.fixture(autouse=True, scope='session')
def prepare_all(client: CouchClient, async_run: Callable):
    response = async_run(client.db_create(db_name))
    assert response.status_code == 201

    response = async_run(client.doc_create_or_update(
        db_name, f'_design/{design_name}', design_body))
    assert response.status_code == 201

    yield

    response = async_run(client.db_delete(db_name))
    assert response.status_code == 200


def test_design_info(client: CouchClient, async_run: Callable):
    result = async_run(client.des_info(db_name, design_name))

    assert result.status_code == 200
    assert result.model.name == 'test_design_doc'
    assert result.model.view_index.get('language') == 'javascript'


def test_view_exec(client: CouchClient, async_run: Callable):
    result = async_run(client.view_exec(db_name, design_name, 'test_view'))

    assert result.status_code == 200
    assert result.model.total_rows == 0
