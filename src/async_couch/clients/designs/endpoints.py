from async_couch import types
from async_couch.clients.designs import responses as resp
from async_couch.http_clients.base_client import BaseEndpoint


class DesignDocEndpoint(BaseEndpoint):
    """
    Implement CouchDB design info API
    """

    __des_doc_endpoint__ = "/{db}/_design/{des_id}/_info"
    """Design Documents info endpoint"""

    async def des_info(self, db: str, des_id: str) -> types.UniversalResponse:
        """
        Obtains information about the specified design document, including
        the index, index size and current status of the design document and
        associated index information.

        Parameters
        ----------
        db: str
            Database name

        des_id: str
            Document id

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
            endpoint=self.__des_doc_endpoint__,
            method=types.HttpMethod.GET,
            statuses={
                200: "Find info",
                404: "Specified database or design was not found",
            },
            path={"db": db, "des_id": des_id},
            response_model=resp.DesignInfoResponse,
        )


class DesignViewEndpoint(BaseEndpoint):
    """
    Implement CouchDB views API
    """

    __des_view_endpoint__ = "/{db}/_design/{des_id}/_view/{view_name}"
    """Design view endpoint"""

    async def view_exec(
        self,
        db: str,
        des_id: str,
        view_name: str,
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
        Executes the specified view function from the specified
        design document.

        Parameters
        ----------
        db
            Database name

        des_id
            Design document name

        view_name
            View function name

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

        if key:
            query["key"] = f'"{key}"'

        if keys:
            query["keys"] = keys

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

        return await self.http_client.make_request(
            endpoint=self.__des_view_endpoint__,
            method=types.HttpMethod.GET,
            statuses={
                200: "Request completed successfully",
                400: "Invalid request",
                401: "Read privilege required",
                404: "Specified database, design document or view is missed",
            },
            query=query,
            path={"db": db, "des_id": des_id, "view_name": view_name},
            response_model=resp.ExecuteViewResponse,
        )
