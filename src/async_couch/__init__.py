from async_couch.clients.documents.endpoints import DocEndpoint, DocAttachmentEndpoint
from async_couch.clients.database.endpoints import DatabaseEndpoint
from async_couch.clients.designs.endpoints import DesignDocEndpoint, DesignViewEndpoint

from async_couch.http_clients import HttpxCouchClient, BaseHttpClient


class CouchClient(
    DocEndpoint,
    DocAttachmentEndpoint,
    DesignDocEndpoint,
    DesignViewEndpoint,
    DatabaseEndpoint,
):
    pass


def get_couch_client(
    https: bool = False,
    host: str = "localhost",
    port: int = 5984,
    request_adapter: BaseHttpClient = HttpxCouchClient,
    user: str | None = None,
    password: str | None = None,
    **kwargs,
) -> CouchClient:
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

    user: str
        Database authentication - username

    password: str
        Database authentication - password

    Returns
    -------
    CouchClient
        CouchDB API realisation

    """
    if any([user is None, password is None]):
        raise ValueError("You need to pass 'auth' tuple or both 'user' and 'password'!")
    kwargs["auth"] = (user, password)

    schema = "http"

    if https:
        schema += "s"

    http_client = request_adapter.get_client(f"{schema}://{host}:{port}", **kwargs)
    return CouchClient(http_client=http_client)
