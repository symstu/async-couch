from dataclasses import dataclass
import typing

from async_couch.types import EmptyResponse

from . import models


@dataclass
class DocumentCreated(EmptyResponse):
    id: str
    # Document ID

    ok: bool
    # Operation status

    rev: str = None
    # Revision info


@dataclass
class ServerResponse(EmptyResponse):
    cluster: models.ClusterObject
    # Cluster information

    compact_running: int
    # Set to true if the database compaction routine is operating on
    # this database.

    db_name: bool
    # The name of the database.

    disk_format_version: int
    # The version of the physical format used for the data when it is stored
    # on disk

    doc_count: int
    # A count of the documents in the specified database

    doc_del_count: int
    # Number of deleted documents

    instance_start_time: str
    # Always "0". (Returned for legacy reasons.)

    purge_seq: str
    # An opaque string that describes the purge state of the database. Do not
    # rely on this string for counting the number of purge operations.

    sizes: models.DatabaseSize

    update_seq: str
    # An opaque string that describes the state of the database. Do not rely
    # on this string for counting the number of updates

    props_partitioned: models.DatabaseProps


@dataclass
class FindResponse(EmptyResponse):
    docs: typing.List[dict]
    # Array of documents matching the search. In each matching document, the
    # fields specified in the fields part of the request body are listed, along
    # with their values.

    warning: str
    # Execution warnings

    bookmark: str
    # An opaque string used for paging. See the bookmark field in the request
    # for usage details.
