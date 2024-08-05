# Preparing test environment

CouchDB does not run in "admin party" mode anymore - you need to configure
the server before using it for tests.

If you already have a working CouchDB on your localhost, just edit `.env` file
providing auth credentials.

If you don't, run:

    docker compose up

Then go to this url:

    http://localhost:5984/_utils/

and configure the instance. Only after this the tests will work.
We're working on using `testcontainters` to fix this.
