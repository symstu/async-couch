class ClusterObject:
    n: int
    # Replicas. The number of copies of every document.

    q: int
    # Shards. The number of range partitions.

    r: int
    #  Read quorum. The number of consistent copies of a document that need
    #  to be read before a successful reply.

    w: int
    # Write quorum. The number of copies of a document that need to be written
    # before a successful reply


class DatabaseSize:
    active: int
    # The size of live data inside the database, in bytes.

    external: int
    # The uncompressed size of database contents in bytes

    file: int
    # The size of the database file on disk in bytes. Views indexes are not
    # included in the calculation


class DatabaseProps:
    partitioned: bool
    # (optional) If present and true, this indicates that the database
    # is partitioned.
