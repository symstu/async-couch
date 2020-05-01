import dataclasses
import typing

from async_couch.types import EmptyResponse


@dataclasses.dataclass
class DocumentExistingResponse(EmptyResponse):
    e_tag: str
    # Document’s revision token


@dataclasses.dataclass
class DocumentDetailedResponse(EmptyResponse):
    _id: str = None
    # Document ID

    _rev: str = None
    # Revision MVCC token

    _deleted: bool = None
    # Deletion flag. Available if document was removed

    _attachments = None
    # Attachment’s stubs. Available if document has any attachments

    _conflicts: typing.List[str] = None
    # List of conflicted revisions. Available if requested with
    # conflicts=true query parameter

    _deleted_conflicts: typing.List[str] = None
    # List of deleted conflicted revisions. Available if requested with
    # deleted_conflicts=true query parameter

    _local_seq: str = None
    # Document’s update sequence in current database. Available if requested
    # with local_seq=true query parameter

    _revs_info: typing.List[str] = None
    #  List of objects with information about local revisions and their
    #  status. Available if requested with open_revs query parameter

    _revisions = None
    # List of local revision tokens without. Available if requested with
    # revs=true query parameter

    _files: dict = None
    # Attachments files

    doc: typing.Dict[str, typing.Any] = None

    @classmethod
    def load(cls, response):
        fields = cls.__dataclass_fields__.keys()
        data = response.json()

        params = dict()

        for field in fields:
            value = data.pop(field, None)

            if value:
                params[field] = value

        params['doc'] = data

        return cls(**params)


@dataclasses.dataclass
class DocumentUpdatingResponse(EmptyResponse):
    id: str = None
    # Document ID

    ok: bool = None
    # Operation status

    rev: str = None
    # Revision MVCC token

