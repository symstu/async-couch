from async_couch import http_clients
from async_couch.clients.documents.endpoints import (
    DocEndpoint,
    DocAttachmentEndpoint
)
from async_couch.clients.database.endpoints import DatabaseEndpoint
from async_couch.clients.designs.endpoints import (
    DesignDocEndpoint,
    DesignViewEndpoint
)

from async_couch.http_clients import HttpxCouchClient, BaseHttpClient


class CouchClient(DocEndpoint,
                  DocAttachmentEndpoint,
                  DesignDocEndpoint,
                  DesignViewEndpoint,
                  DatabaseEndpoint):

    async def close(self):
        await self.http_client.aclose()


def get_couch_client(https: bool = False,
                     host: str = 'localhost',
                     port: int = 5984,
                     request_adapter: BaseHttpClient = HttpxCouchClient,
                     **kwargs) -> CouchClient:
    """
    Initialize CouchClient

    Parameters
    ----------
    https: bool = False
        Schema type. Use https if value is True

    host: str = 'localhost'
        CouchDB host

    port: int = 5984
        CouchDB port

    request_adapter: BaseHttpClient = HttpxCouchClient
        Http client adapter

    Returns
    -------
    CouchClient
        CouchDB API realisation

    """
    schema = 'http'

    if https:
        schema += 's'

    url = f'{schema}://{host}'
    if port:
        url += f':{port}'

    http_client = request_adapter.get_client(url, **kwargs)
    return CouchClient(http_client=http_client)
