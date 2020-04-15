import asyncio
import pytest
import typing

from async_couch import get_couch_client, CouchClient


@pytest.fixture(scope='session')
def loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def async_run(loop: asyncio.AbstractEventLoop) -> typing.Callable:
    return loop.run_until_complete


@pytest.fixture(scope='session')
def client() -> CouchClient:
    return get_couch_client()
