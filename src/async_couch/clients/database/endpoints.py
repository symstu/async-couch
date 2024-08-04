from async_couch import types
from async_couch.clients.designs.responses import ExecuteViewResponse
from async_couch.http_clients.base_client import BaseEndpoint
from . import responses as resp


class DatabaseEndpoint(BaseEndpoint):
    """
    Implement CouchDB database API
    """

    __db_endpoint__ = "/{db}"
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
            statuses={200: "Database exists", 404: "Requested database not found"},
            path={"db": db},
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
                200: "Request completed successfully",
                404: "Requested database not found",
            },
            path={"db": db},
        )

    async def db_create(
        self, db: str, q: int = 8, n: int = 3, partitioned: bool = False
    ):
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
                201: "Database created successfully (quorum is met)",
                202: "Accepted (at least by one node)",
                400: "Invalid database name",
                412: "Database already exists",
            },
            path={"db": db},
            query={"q": q, "n": n, "partitioned": partitioned},
        )

    async def db_create_doc(
        self, db: str, doc: dict, batch: str = None
    ) -> types.UniversalResponse:
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
                201: "Document created and stored on disk",
                202: "Document data accepted, but not yet stored on disk",
                400: "Invalid database name",
                401: "Write privileges required",
                404: "Database does not exist",
                409: "A Conflicting Document with same ID already exists",
            },
            path={"db": db},
            query={"batch": "ok"} if batch else None,
            json_data=doc,
            response_model=resp.DocumentCreated,
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
                200: "Database removed successfully",
                202: "Accepted (deleted by at least one of the nodes)",
                400: "Invalid database name or forgotten document id by " "accident",
                401: "CouchDB Server Administrator privileges required",
                404: "Database doesn’t exist or invalid database name",
            },
            path={"db": db},
        )

    async def db_all_docs(
        self,
        db: str,
        conflicts: bool = False,
        descending: bool = False,
        end_key: dict = None,
        end_key_doc_id: str = None,
        group: bool = False,
        group_level: int = None,
        include_docs: bool = False,
        attachments: bool = False,
        att_encoding_info: bool = False,
        inclusive_end: bool = True,
        key: dict = None,
        keys: list = None,
        limit: int = None,
        reduce: bool = True,
        skip: int = 0,
        sort: bool = True,
        stable: bool = False,
        stale: str = None,
        start_key: dict = None,
        start_key_doc_id: str = None,
        update: bool = True,
        update_seq: bool = False,
    ) -> types.UniversalResponse:
        """
        POST _all_docs functionality supports identical parameters and
        behavior as specified in the GET /{db}/_all_docs API but allows for
        the query string parameters to be supplied as keys in a JSON object
        in the body of the POST request.
        Parameters
        ----------
        db
            Database name

        conflicts: bool = False
            Include conflicts information in response. Ignored if
            include_docs isn’t true

        descending: bool = False
            Return the documents in descending order by key

        end_key: dict = None
            Stop returning records when the specified key is reached

        end_key_doc_id: str = None
            Alias for endkey_docid

        group: bool = False
            Group the results using the reduce function to a group or single
            row. Implies reduce is true and the maximum group_level

        group_level: int = None
            Specify the group level to be used. Implies group is true

        include_docs: bool = False
            Include the associated document with each row

        attachments: bool = False
            Include the Base64-encoded content of attachments in the documents
            that are included if include_docs is true. Ignored if
            include_docs isn’t true.

        att_encoding_info: bool = False
            Include encoding information in attachment stubs if
            include_docs is true and the particular attachment is
            compressed. Ignored if include_docs isn’t true

        inclusive_end: bool = False
            Specifies whether the specified end key should be included in
            the result

        key: dict = None
            Return only documents that match the specified key

        keys: list = None
            Return only documents where the key matches one of the keys
            specified in the array

        limit: int = None
            Limit the number of the returned documents to the specified number

        reduce: bool = True
             Use the reduction function. Default is true when a reduce
             function is defined

        skip: int = 0
            Skip this number of records before starting to return the results

        sort: bool = False
            Sort returned rows (see Sorting Returned Rows). Setting this to
            false offers a performance boost. The total_rows and offset
            fields are not available when this is set to false.

        stable: bool = False
            Whether or not the view results should be returned from a
            stable set of shards

        stale: str = None
            Allow the results from a stale view to be used. Supported values:
            ok, update_after and false. ok is equivalent to
            stable=true&update=false. update_after is equivalent to
            stable=true&update=lazy. false is equivalent to
            stable=false&update=true

        start_key: dict = None
            Return records starting with the specified key.

        start_key_doc_id: str = None
            Return records starting with the specified document ID.
            Ignored if startkey is not set

        update: bool = True
            Whether or not the view in question should be updated prior to
            responding to the user. Supported values: true, false, lazy

        update_seq: bool = False
            Whether to include in the response an update_seq value indicating
            the sequence id of the database the view reflects

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        query = dict()

        if conflicts:
            query["conflicts"] = conflicts

        if descending:
            query["descending"] = descending

        if end_key:
            query["end_key"] = end_key

        if end_key_doc_id:
            query["end_key_doc_id"] = end_key_doc_id

        if group:
            query["group"] = group

        if group_level:
            query["group_level"] = group_level

        if include_docs:
            query["include_docs"] = include_docs

        if attachments:
            query["attachments"] = attachments

        if att_encoding_info:
            query["att_encoding_info"] = att_encoding_info

        if not inclusive_end:
            query["inclusive_end"] = inclusive_end

        if limit:
            query["limit"] = limit

        if not reduce:
            query["reduce"] = reduce

        if skip:
            query["skip"] = skip

        if not sort:
            query["sorted"] = sort

        if stable:
            query["stable"] = stable

        if stale:
            query["stale"] = stale

        if start_key:
            query["start_key"] = start_key

        if start_key_doc_id:
            query["start_key_doc_id"] = start_key_doc_id

        if update != "true":
            query["update"] = update

        if update_seq:
            query["update_seq"] = update_seq

        json_data = dict()

        if key:
            json_data["key"] = f'"{key}"'
        elif keys:
            json_data["keys"] = keys

        return await self.http_client.make_request(
            endpoint="/{db}/_all_docs",
            method=types.HttpMethod.POST,
            statuses={
                200: "Request completed successfully",
                400: "Invalid request",
                401: "Read privilege required",
                404: "Specified database, design document or view is missed",
            },
            query=query,
            path={"db": db},
            json_data=json_data,
            response_model=ExecuteViewResponse,
        )

    async def db_design_docs(
        self,
        db: str,
        conflicts: bool = False,
        descending: bool = False,
        end_key: str = None,
        end_key_doc_id: str = None,
        include_docs: bool = False,
        inclusive_end: bool = True,
        key: str = None,
        keys: str = None,
        limit: int = None,
        skip: int = 0,
        start_key: str = None,
        start_key_doc_id: str = None,
        update_seq: bool = False,
    ) -> types.UniversalResponse:
        """
        POST _all_docs functionality supports identical parameters and behavior
        as specified in the GET /{db}/_all_docs API but allows for the query
        string parameters to be supplied as keys in a JSON object in the body
        of the POST request.
        -------------------

        db
            Database name

        conflict: bool = false
            Includes conflicts information in response. Ignored if include_docs
             isn’t true.

        end_key: str = none
            Stop returning records when the specified design document ID is
            reached.

        end_key_doc_id: str = none
            Stop returning records when the specified design document ID is
            reached.

        include_docs: bool = false
            Include the full content of the design documents in the return.

        inclusive_end: bool = true
            Specifies whether the specified end key should be included in the
            result.

        key: str = none
            Return only design documents that match the specified key.

        keys: str = none
            Return only design documents that match the specified keys.

        limit: int = none
            Limit the number of the returned design documents to the specified
            number.

        skip: int = 0
            Skip this number of records before starting to return the results.

        start_key: str = none
            Return records starting with the specified key.

        start_key_doc_id: str = none
             Return records starting with the specified design document ID.

        update_seq: bool = false
            Response includes an update_seq value indicating which sequence id
            of the underlying database the view reflects.

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """

        query = dict()

        if conflicts:
            query["conflicts"] = conflicts
        if descending:
            query["descending"] = descending
        if end_key:
            query["end_key"] = end_key
        if end_key_doc_id:
            query["end_key_doc_id"] = end_key_doc_id
        if include_docs:
            query["include_docs"] = include_docs
        if not inclusive_end:
            query["inclusive_end"] = inclusive_end
        if limit:
            query["limit"] = limit
        if skip:
            query["slip"] = skip
        if start_key:
            query["start_key"] = start_key
        if start_key_doc_id:
            query["start_key_doc_id"] = start_key_doc_id
        if update_seq:
            query["update_seq"] = update_seq

        json_data = dict()

        if key:
            json_data["key"] = f"{key}"
        elif keys:
            json_data["keys"] = keys

        return await self.http_client.make_request(
            endpoint="/{db}/_design_docs",
            method=types.HttpMethod.POST,
            statuses={
                200: "Request completed successfully",
                404: "Requested database not found",
            },
            query=query,
            path={"db": db},
            json_data=json_data,
            response_model=ExecuteViewResponse,
        )

    async def db_bulk_get(
        self, db: str, revs: bool = None, id: int = None
    ) -> types.UniversalResponse:
        """
        This method can be called to query several documents in bulk. It is
        well suited for fetching a specific revision of documents, as
        replicators do for example, or for getting revision history.
        --------------------------

        db
            Database name

        revs: bool = None
            Give the revisions history

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """

        query = dict()

        if revs:
            query["revs"] = revs

        result = dict()

        if id:
            result["id"] = id

        return await self.http_client.make_request(
            endpoint="/db/_bulk_get",
            method=types.HttpMethod.POST,
            statuses={
                200: "Request completed successfully",
                400: "The request provided invalid JSON data or invalid "
                "query parameter",
                401: "Read permission required",
                404: "Invalid database name",
                415: "Bad Content-Type value",
            },
            query=query,
            path={"db": db},
            json_data=result,
            response_model=ExecuteViewResponse,
        )

    async def db_bulk_docs(
        self, db: str, docs: list, new_edits: bool = True
    ) -> types.UniversalResponse:
        """
        The bulk document API allows you to create and update multiple
        documents at the same time within a single request. The basic operation
        is similar to creating or updating a single document, except that you
        batch the document structure and information.
        When creating new documents the document ID (_id) is optional.
        For updating existing documents, you must provide the document ID,
        revision information (_rev), and new document values.
        In case of batch deleting documents all fields as document ID, revision information and deletion status (_deleted) are required.
        ----------------

        db
            Database name

        docs: list
            List of document objects

        new_edits: bool=True
            If false, prevents the database from assigning them new revision
            IDs

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """

        query = dict()

        if docs:
            query["docs"] = docs
        if new_edits:
            query["new_edits"] = new_edits

        return await self.http_client.make_request(
            endpoint="/db/_bulk_docs",
            method=types.HttpMethod.POST,
            statuses={
                201: "Document(s) have been created or updated",
                401: "The request provided invalid JSON data",
                404: "Requested database not found",
            },
            query=query,
            path={"db": db},
            response_model=ExecuteViewResponse,
        )

    async def db_find(
        self,
        db: str,
        selector: dict,
        limit: int = 25,
        skip: int = None,
        sort: dict = None,
        fields: dict = None,
        use_index: dict = None,
        r: int = 1,
        bookmark: str = None,
        update: bool = True,
        stable: bool = None,
        stale: str = None,
        execution_stats: bool = False,
    ) -> ExecuteViewResponse:
        """
        Find documents using a declarative JSON querying syntax. Queries can
        use the built-in _all_docs index or custom indexes, specified using the
         _index endpoint.
        ------------------------

        db
            Database name

        selector: dict
             JSON object describing criteria used to select documents. More
             information provided in the section on selector syntax. Required

        limit: int = 25
            Maximum number of results returned.

        skip: int = None
            Skip the first ‘n’ results, where ‘n’ is the value specified.

        sort: dict = None
            JSON array following sort syntax.

        fields: dict = None
            JSON array specifying which fields of each object should be
            returned. If it is omitted, the entire object is returned. More
            information provided in the section on filtering fields.

        use_index: dict = None
             Instruct a query to use a specific index. Specified either as
             "<design_document>" or ["<design_document>", "<index_name>"].

        r: int = 1
            Read quorum needed for the result. This defaults to 1, in which
            case the document found in the index is returned. If set to a
            higher value, each document is read from at least that many
            replicas before it is returned in the results. This is likely to
            take more time than using only the document stored locally with
            the index.

        bookmark: str = None
            A string that enables you to specify which page of results you
            require. Used for paging through result sets. Every query returns
            an opaque string under the bookmark key that can then be passed
            back in a query to get the next page of results. If any part of the
            selector query changes between requests, the results are undefined.

        update: bool = True
            Whether to update the index prior to returning the result.

        stable: bool = None
            Whether or not the view results should be returned from a “stable”
            set of shards.

        stale: str = None
            Combination of update=false and stable=true options. Possible
            options: "ok", false (default).

        execution_stats: bool = False
            Include execution statistics in the query response.

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """

        query = dict()

        if limit:
            query["limit"] = limit
        if skip:
            query["skip"] = skip
        if sort:
            query["sort"] = sort
        if fields:
            query["fields"] = fields
        if use_index:
            query["use_index"] = use_index
        if r:
            query["r"] = r
        if bookmark:
            query["bookmark"] = bookmark
        if update:
            query["update"] = update
        if stable:
            query["stable"] = stable
        if stale:
            query["stale"] = stale
        if execution_stats:
            query["execution_stats"] = execution_stats

        json_data = dict()

        if selector:
            json_data["selector"] = selector

        return await self.http_client.make_request(
            endpoint="/db/_find",
            method=types.HttpMethod.POST,
            statuses={
                200: "Request completed successfully",
                400: "Invalid request",
                401: "Read permission required",
                404: "Requested database not found",
                500: "Query execution error",
            },
            query=query,
            path={"db": db},
            json_data=json_data,
            response_model=ExecuteViewResponse,
        )
