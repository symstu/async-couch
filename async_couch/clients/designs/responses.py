import typing

from dataclasses import dataclass
from async_couch.types import EmptyResponse


@dataclass
class SizeObj:
    active: int
    """The size of live data inside the view, in bytes"""

    external: int
    """The uncompressed size of view contents in bytes"""

    file: int
    """Size in bytes of the view as stored on disk"""


@dataclass
class DesignViewIndex:
    compact_running: bool
    """Indicates whether a compaction routine is currently
    running on the view"""

    sizes: SizeObj
    """Sized of stored data"""

    language: str
    """Language for the defined views"""

    purge_seq: int
    """The purge sequence that has been processed"""

    signature: str
    """MD5 signature of the views for the design document"""

    update_seq: int or str
    """The update sequence of the corresponding database that has been
    indexed"""

    updater_running: bool
    """Indicates if the view is currently being updated"""

    waiting_clients: int
    """Number of clients waiting on views from this design document"""

    waiting_commit: bool
    """Indicates if there are outstanding commits to the underlying database
    that need to processed"""


@dataclass
class DesignInfoResponse(EmptyResponse):
    name: str
    """Design document name"""

    view_index: DesignViewIndex
    """View Index Information"""


@dataclass
class ExecuteViewRow:
    id: str
    key: str
    value: dict


@dataclass
class ExecuteViewResponse(EmptyResponse):
    offset: int = None
    """Offset where the document list started"""

    rows: typing.List[ExecuteViewRow] = None
    """Array of view row objects. By default the information returned
    contains only the document ID and revision"""

    total_rows: int = None
    """Number of documents in the database/view"""

    update_seq: dict = None
    """Current update sequence for the database."""
