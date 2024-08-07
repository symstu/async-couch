# Async-Couch

![Logo](docs/source/_static/logo.jpg)
![Documentation Status](https://readthedocs.org/projects/async-couch/badge/?version=latest)
![Python package](https://github.com/symstu/async-couch/workflows/testing/badge.svg?branch=master)
![PyPI version](https://badge.fury.io/py/async-couch.svg)

## Resources
   * [Documentation](https://async-couch.readthedocs.io/en/latest/)

> This is simple asynchronous python CouchDB client that works with
> aiohttp, httpx and able to be adopted easily to any other http client.

### Requirements:
   * >= Python 3.11

### Allowed http client
   * [aiohttp](https://docs.aiohttp.org/en/stable/>)
   * [httpx](https://www.python-httpx.org/>)

### How to install
```bash
pip install async-couch
```

### Get Started
```python
   import asyncio

   from async_couch import get_couch_client
   from async_couch.http_clients import HttpxCouchClient


   async def example(client, doc_id: str):
      await client.db_create('test_index')
      await client.doc_create_or_update('test_index', doc_id, dict(val=1))

      response = await client.doc_get('test_index', response.model._id)
      assert response.model._id == doc_id

      await client.attachment_upload(
         'test_index', response.model._id, 'attachment_name', 'text/plain', b'\0')

   if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      client = get_couch_client(request_adapter=HttpxCouchClient)

      loop.run_until_complete(example(client, 'document_name'))
```

### ToDo
* Rest endpoints
* Aiohttp adapter
