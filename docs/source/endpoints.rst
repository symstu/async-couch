Endpoints
============
Full description of all available methods

.. toctree::
    :name: Endpoints
    :maxdepth: 2

    couch_client
    databases
    documents

.. code-block:: python

    class CouchClient(DocEndpoint,
                      DocAttachmentEndpoint,
                      DatabaseEndpoint):
    pass


.. note::
    As you can see, CouchClient uses multiple inheritance for good reading,
    so you don't need to read full documentation but find necessary
    API realisation in specific class.

.. note::
    Async-Couch uses classes and methods description from
    `official CouchDB <https://docs.couchdb.org/>`_ documentation.
