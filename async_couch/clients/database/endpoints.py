import typing

from async_couch import types
from async_couch.clients.designs.responses import ExecuteViewResponse
from async_couch.http_clients.base_client import BaseEndpoint
from . import responses as resp


class DatabaseEndpoint(BaseEndpoint):
    """
    Implement CouchDB database API
    """

    __db_endpoint__ = '/{db}'
    """Database endpoint"""

    async def db_exists(self, db: str) -> types.UniversalResponse:
        """
        Returns the HTTP Headers containing a minimal amount of information
        about the specified database. Since the response body is empty, using
        the HEAD method is a lightweight way to check if the database exists
        already or not.

        Parameters
        ----------
        db: str
            Database name

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        return await self.http_client.make_request(
            endpoint=self.__db_endpoint__,
            method=types.HttpMethod.HEAD,
            statuses={
                200: 'Database exists',
                404: 'Requested database not found'
            },
            path={'db': db}
        )

    async def db_info(self, db: str) -> resp.ServerResponse:
        """
        Gets information about the specified database.

        Parameters
        ----------
        db: str
            Database name

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        return await self.http_client.make_request(
            endpoint=self.__db_endpoint__,
            method=types.HttpMethod.GET,
            statuses={
                200: 'Request completed successfully',
                404: 'Requested database not found'
            },
            path={'db': db}
        )

    async def db_create(self,
                        db: str,
                        q: int = 8,
                        n: int = 3,
                        partitioned: bool = False):
        """
        Creates a new database. The database name {db} must be composed by
        following next rules:

            * Name must begin with a lowercase letter (a-z)
            * Lowercase characters (a-z)
            * Digits (0-9)
            * Any of the characters _, $, (, ), +, -, and /.

        If you’re familiar with Regular Expressions, the rules above could
        be written as ^[a-z][a-z0-9_$()+/-]*$.

        Parameters
        ----------
        db: str
            Database name

        n: int
            Replicas. The number of copies of the database in the cluster.
            The default is 3, unless overridden in the cluster config

        q: int
            Shards, aka the number of range partitions. Default is 8,
            unless overridden in the cluster config.

        partitioned: bool = False
            Whether to create a partitioned database.

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        return await self.http_client.make_request(
            endpoint=self.__db_endpoint__,
            method=types.HttpMethod.PUT,
            statuses={
                201: 'Database created successfully (quorum is met)',
                202: 'Accepted (at least by one node)',
                400: 'Invalid database name',
                412: 'Database already exists'
            },
            path={'db': db},
            query={'q': q, 'n': n, 'partitioned': partitioned}
        )

    async def db_create_doc(self,
                            db: str,
                            doc: dict,
                            batch: str = None) -> types.UniversalResponse:
        """
        Creates a new document in the specified database, using the supplied
        JSON document structure. If the JSON structure includes the _id field,
        then the document will be created with the specified document ID.

        If the _id field is not specified, a new unique ID will be generated,
        following whatever UUID algorithm is configured for that server.

        Parameters
        ----------
        db: str
            Database name
        doc: dict
            document to create
        batch: str = None
            Stores document in batch mode. Possible values: `ok`

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        return await self.http_client.make_request(
            endpoint=self.__db_endpoint__,
            method=types.HttpMethod.POST,
            statuses={
                201: 'Document created and stored on disk',
                202: 'Document data accepted, but not yet stored on disk',
                400: 'Invalid database name',
                401: 'Write privileges required',
                404: 'Database does not exist',
                409: 'A Conflicting Document with same ID already exists'
            },
            path={'db': db},
            query={'batch': 'ok'} if batch else None,
            json_data=doc,
            response_model=resp.DocumentCreated
        )

    async def db_delete(self, db: str):
        """
        Deletes the specified database, and all the documents and attachments
        contained within it.

        Parameters
        ----------
        db: str
            Database name

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        return await self.http_client.make_request(
            endpoint=self.__db_endpoint__,
            method=types.HttpMethod.DELETE,
            statuses={
                200: 'Database removed successfully',
                202: 'Accepted (deleted by at least one of the nodes)',
                400: 'Invalid database name or forgotten document id by '
                     'accident',
                401: 'CouchDB Server Administrator privileges required',
                404: 'Database doesn’t exist or invalid database name'
            },
            path={'db': db},
        )

    async def db_all_docs(self, db: str, keys: typing.List[str] = None):
        """
        Executes the built-in _all_docs view, returning all of the documents
        in the database. With the exception of the URL parameters (described
        below), this endpoint works identically to any other view. Refer to
        the view endpoint documentation for a complete description of the
        available query parameters and the format of the returned data.

        POST _all_docs functionality supports identical parameters and
        behavior as specified in the GET /{db}/_all_docs API but allows for
        the query string parameters to be supplied as keys in a JSON object
        in the body of the POST request.

        Parameters
        ----------
        keys: typing.List[str]
            doc id

        db: str
            Database name

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        if not keys:
            keys = []

        json_data = dict(keys=keys)

        return await self.http_client.make_request(
            endpoint='/{db}/_all_docs',
            method=types.HttpMethod.POST,
            statuses={
                200: 'Request completed successfully',
                404: 'Requested database not found'
            },
            json_data=json_data,
            path={'db': db},
            response_model=ExecuteViewResponse
        )
