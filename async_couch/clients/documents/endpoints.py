import json
import typing

from async_couch import types
from async_couch.http_clients.base_client import BaseEndpoint
from async_couch.clients.database.responses import DocumentCreated
from async_couch.clients.documents import responses as resp
from async_couch.utils.content_types import MultipartRelated, \
    MultipartRelatedAttachment, multipart_boundary


class DocEndpoint(BaseEndpoint):
    """
    Implement CouchDB documents API
    """

    __doc_endpoint__ = '/{db}/{doc_id}'
    """Documents endpoint"""

    async def doc_exists(self,
                         db: str,
                         doc_id: str) -> types.UniversalResponse:
        """
        Returns the HTTP Headers containing a minimal amount of information
        about the specified document. The method supports the same query
        arguments as the GET /{db}/{docid} method, but only the header
        information (including document size, and the revision as an ETag),
        is returned.

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
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
            endpoint=self.__doc_endpoint__,
            method=types.HttpMethod.HEAD,
            statuses={
                200: 'Document exists',
                304: 'Document wasn’t modified since specified revision',
                401: 'Read privilege required',
                404: 'Document not found'
            },
            path={'db': db, 'doc_id': doc_id},
            response_model=resp.DocumentExistingResponse
        )

    async def doc_get(self,
                      db: str,
                      doc_id: str,
                      attachments: bool = False,
                      att_encoding_info: bool = False,
                      attributes_since: str = None,
                      conflicts: bool = False,
                      deleted_conflicts: bool = False,
                      latest: bool = False,
                      local_seq: bool = False,
                      meta: bool = False,
                      open_revs: str = None,
                      rev: str = None,
                      revs: bool = False,
                      revs_info: bool = False) -> types.UniversalResponse:
        """
        Gets information about the specified database.

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        attachments: bool = False
            Includes attachments bodies in response

        att_encoding_info: bool = False
            Includes encoding information in attachment
            stubs if the particular attachment is compressed

        attributes_since: str = None
            Includes attachments only since specified
            revisions. Does not includes attachments for specified revisions

        conflicts: bool = False
            Includes information about conflicts in document

        deleted_conflicts: bool = False
            Includes information about deleted
            conflicted revisions

        latest: bool = False
            Forces retrieving latest “leaf” revision, no matter
            what rev was requested.

        local_seq: bool = False
            Includes last update sequence for the document

        meta: bool = False
            Acts same as specifying all conflicts, deleted_conflicts
            and revs_info query parameters

        open_revs: str = None
            Retrieves documents of specified leaf revisions.
            Additionally, it accepts value as all to return all leaf revisions

        rev: str = None
            Retrieves document of specified revision

        revs: bool = False
            Includes list of all known document revisions

        revs_info: bool = False
            Includes detailed information for all known document revisions
        """
        query = dict()

        if attachments:
            query['attachments'] = attachments

        if att_encoding_info:
            query['att_encoding_info'] = att_encoding_info

        if attributes_since:
            query['atts_since'] = attributes_since

        if conflicts:
            query['conflicts'] = conflicts

        if deleted_conflicts:
            query['deleted_conflicts'] = deleted_conflicts

        if latest:
            query['latest'] = latest

        if local_seq:
            query['local_seq'] = local_seq

        if meta:
            query['local_seq'] = local_seq

        if open_revs:
            query['open_revs'] = local_seq

        if rev:
            query['rev'] = local_seq

        if revs:
            query['revs'] = local_seq

        if revs_info:
            query['revs_info'] = local_seq

        return await self.http_client.make_request(
            endpoint=self.__doc_endpoint__,
            method=types.HttpMethod.GET,
            statuses={
                200: 'Request completed successfully',
                304: 'Document wasn’t modified since specified revision',
                400: 'Bad request',
                401: 'Read privilege required',
                404: 'Document not found'
            },
            query=query,
            path={'db': db, 'doc_id': doc_id},
            response_model=resp.DocumentDetailedResponse
        )

    async def doc_create_or_update(self,
                                   db: str,
                                   doc_id: str,
                                   doc: dict,
                                   rev: str = None,
                                   batch: str = None,
                                   new_edits: bool = True,
                                   attachments: typing.List[MultipartRelatedAttachment] = None) -> types.UniversalResponse:
        """
        The PUT method creates a new named document, or creates a new
        revision of the existing document. Unlike the POST /{db}, you must
        specify the document ID in the request URL.

        When updating an existing document, the current document revision
        must be included in the document (i.e. the request body), as the
        rev query parameter, or in the If-Match request header.

        Parameters
        ----------
        attachments: List[Attachment]
            For bulk upload. In this case it should be sent as multipart
            related

        db: str
            Database name

        doc_id: str
            Document id

        doc: dic
            Document data

        rev: str = None
            Document’s revision if updating an existing document

        batch: str = None
            Stores document in batch mode. Possible values: ok

        new_edits: bool = True
            Prevents insertion of a conflicting document.
            Possible values: true (default) and false. If false, a
            well-formed _rev must be included in the document.
            new_edits=false is used by the replicator to insert documents
            into the target database even if that leads to the creation
            of conflicts. Optional

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

        if rev:
            query['rev'] = rev

        if batch:
            query['batch'] = batch

        if not new_edits:
            query['new_edits'] = new_edits

        kwargs = dict(
            endpoint=self.__doc_endpoint__,
            method=types.HttpMethod.PUT,
            statuses={
                201: 'Document created and stored on disk',
                202: 'Document data accepted, but not yet stored on disk',
                400: 'Invalid request body or parameters',
                401: 'Read privilege required',
                404: 'Specified database or document ID doesn’t exists',
                409: 'Document with the specified ID already exists or '
                     'specified revision is not latest for target document'
            },
            path={'db': db, 'doc_id': doc_id},
            query=query,
            response_model=resp.DocumentUpdatingResponse
        )

        if not attachments:
            kwargs['json_data'] = doc
            return await self.http_client.make_request(**kwargs)

        json_part = MultipartRelatedAttachment()
        json_part.mime_type = b'application/json'

        json_data = dict(_attachments=dict())
        json_data.update(**doc)

        for attachment in attachments:
            attachment_name = attachment.name.decode()
            json_data['_attachments'][attachment_name] = attachment.as_dict

        json_part.data = json.dumps(json_data).encode()

        content_type = f'multipart/related;boundary="{multipart_boundary[2:].decode()}"'
        kwargs['data'] = MultipartRelated.dump([json_part] + attachments)
        kwargs['headers'] = {'Content-Type': content_type}

        return await self.http_client.make_request(**kwargs)

    async def doc_delete(self,
                         db: str,
                         doc_id: str,
                         rev: str,
                         batch: str = None) -> types.UniversalResponse:
        """
        Marks the specified document as deleted by adding a field _deleted
        with the value true. Documents with this field will not be returned
        within requests anymore, but stay in the database. You must supply
        the current (latest) revision, either by using the rev parameter or
        by using the If-Match header to specify the revision.

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        rev: str
            Actual document’s revision

        batch: str = None
            Stores document in batch mode Possible values: ok

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

        if batch:
            query['batch'] = batch

        if rev:
            query['rev'] = rev

        return await self.http_client.make_request(
            endpoint=self.__doc_endpoint__,
            method=types.HttpMethod.DELETE,
            statuses={
                200: 'Document successfully removed',
                202: 'Request was accepted, but changes are not yet '
                     'stored on disk',
                400: 'Invalid request body or parameters',
                401: 'Write privileges required',
                404: 'Specified database or document ID doesn’t exists',
                409: 'Specified revision is not the latest for target document'
            },
            path={'db': db, 'doc_id': doc_id},
            query=query,
            response_model=DocumentCreated
        )

    async def doc_copy(self,
                       db: str,
                       doc_id: str,
                       destination: str,
                       rev: str = None,
                       batch: str = None) -> types.UniversalResponse:
        """
        The COPY (which is non-standard HTTP) copies an existing document to
        a new or existing document. Copying a document is only possible
        within the same database.

        The source document is specified on the request line, with the
        Destination header of the request specifying the target document.

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        destination: str
            Destination document. Must contain the target document ID, and
            optionally the target document revision, if copying to an
            existing document

        rev: str
            Actual document’s revision

        batch: str = None
            Stores document in batch mode Possible values: ok

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        headers = dict(Destination=f'{destination}')
        query = dict()

        if batch:
            query['batch'] = batch

        if rev:
            query['rev'] = rev

        return await self.http_client.make_request(
            endpoint=self.__doc_endpoint__,
            method=types.HttpMethod.COPY,
            statuses={
                201: 'Document successfully created',
                202: 'Request was accepted, but changes are not yet '
                     'stored on disk',
                400: 'Invalid request body or parameters',
                401: 'Read or write privileges required',
                404: 'Specified database, document ID or revision '
                     'doesn’t exists',
                409: 'Specified revision is not the latest for target document'
            },
            path={'db': db, 'doc_id': doc_id},
            headers=headers,
            query=query,
            response_model=DocumentCreated
        )


class DocAttachmentEndpoint(BaseEndpoint):
    """
    Implement CouchDB document attachments API
    """

    __doc_attachment_endpoint__: str = '/{db}/{doc_id}/{att_id}'
    """Attachments endpoint"""

    async def attachment_exists(self,
                                db: str,
                                doc_id: str,
                                attachment_id: str,
                                rev: str = None) -> types.UniversalResponse:
        """
        Returns the HTTP headers containing a minimal amount of information
        about the specified attachment. The method supports the same query
        arguments as the GET /{db}/{docid}/{attname} method, but only the
        header information (including attachment size, encoding and the
        MD5 hash as an ETag), is returned

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        attachment_id: str
            Attachment name

        rev: str = None
            Actual document’s revision

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

        if rev:
            query['rev'] = rev

        return await self.http_client.make_request(
            endpoint=self.__doc_attachment_endpoint__,
            method=types.HttpMethod.HEAD,
            statuses={
                200: 'Attachment exists',
                401: 'Read privilege required',
                404: 'Specified database, document or attachment was not found'
            },
            path={'db': db, 'doc_id': doc_id, 'att_id': attachment_id},
            query=query,
            response_model=DocumentCreated
        )

    async def attachment_get(self,
                             db: str,
                             doc_id: str,
                             attachment_id: str,
                             rev: str = None) -> types.UniversalResponse:
        """
        Returns the file attachment associated with the document. The raw
        data of the associated attachment is returned (just as if you were
        accessing a static file. The returned Content-Type will be the same
        as the content type set when the document attachment was submitted
        into the database.


        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        attachment_id: str
            Attachment name

        rev: str = None
            Actual document’s revision

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

        if rev:
            query['rev'] = rev

        return await self.http_client.make_request(
            endpoint=self.__doc_attachment_endpoint__,
            method=types.HttpMethod.GET,
            statuses={
                200: 'Attachment exists',
                401: 'Read privilege required',
                404: 'Specified database, document or attachment was not found'
            },
            path={'db': db, 'doc_id': doc_id, 'att_id': attachment_id},
            query=query
        )

    async def attachment_upload(self,
                                db: str,
                                doc_id: str,
                                attachment_id: str,
                                content_type: str,
                                data: bytes,
                                rev: str) -> types.UniversalResponse:
        """
        Uploads the supplied content as an attachment to the specified
        document. The attachment name provided must be a URL encoded string.
        You must supply the Content-Type header, and for an existing document
        you must also supply either the rev query argument or the If-Match
        HTTP header. If the revision is omitted, a new, otherwise empty
        document will be created with the provided attachment, or a conflict
         will occur.

        If case when uploading an attachment using an existing attachment
        name, CouchDB will update the corresponding stored content of the
        database. Since you must supply the revision information to add an
        attachment to the document, this serves as validation to update
        the existing attachment.

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        attachment_id: str
            Attachment name

        content_type: str
            Attachment MIME type

        data: bytes
            Uploading file data

        rev: str = None
            Actual document’s revision

        Returns
        ----------
        `UniversalResponse`
            Operating result

        Raises
        ----------
        exc.CouchResponseError:
            If server error occurred
        """
        headers = dict()
        headers['Content-Type'] = content_type

        query = dict()

        if rev:
            query['rev'] = rev

        return await self.http_client.make_request(
            endpoint=self.__doc_attachment_endpoint__,
            method=types.HttpMethod.PUT,
            statuses={
                201: 'Attachment created and stored on disk',
                202: 'Request was accepted, but changes are not yet stored '
                     'on disk',
                400: 'Invalid request body or parameters',
                401: 'Write privilege required',
                404: 'Specified database, document or attachment was '
                     'not found',
                409: 'Document’s revision wasn’t specified or it’s not '
                     'the latest'
            },
            path={'db': db, 'doc_id': doc_id, 'att_id': attachment_id},
            query=query,
            data=data,
            response_model=DocumentCreated
        )

    async def attachment_delete(self,
                                db: str,
                                doc_id: str,
                                attachment_id: str,
                                rev: str = None) -> types.UniversalResponse:
        """
        Deletes the attachment with filename {attname} of the specified doc.
        You must supply the rev query parameter or If-Match with the current
        revision to delete the attachment.

        Parameters
        ----------
        db: str
            Database name

        doc_id: str
            Document id

        attachment_id: str
            Attachment name

        rev: str = None
            Actual document’s revision

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

        if rev:
            query['rev'] = rev

        return await self.http_client.make_request(
            endpoint=self.__doc_attachment_endpoint__,
            method=types.HttpMethod.DELETE,
            statuses={
                200: 'Attachment successfully removed',
                202: 'Request was accepted, but changes are not yet stored '
                     'on disk',
                400: 'Invalid request body or parameters',
                401: 'Write privilege required',
                404: 'Specified database, document or attachment was '
                     'not found',
                409: 'Document’s revision wasn’t specified or it’s not '
                     'the latest'
            },
            path={'db': db, 'doc_id': doc_id, 'att_id': attachment_id},
            query=query,
            response_model=DocumentCreated
        )
