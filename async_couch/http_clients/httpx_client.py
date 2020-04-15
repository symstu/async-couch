import httpx

from typing import Dict

from async_couch import types
from async_couch.http_clients.base_client import BaseHttpClient


class HttpxCouchClient(BaseHttpClient, httpx.AsyncClient):
    request_method = httpx.AsyncClient.request

    @classmethod
    def get_client(cls, couch_endpoint_url):
        return cls(base_url=couch_endpoint_url)

    @staticmethod
    def prepare_request(endpoint: str,
                        method: types.HttpMethod,
                        path: Dict[str, str] = None,
                        query: Dict[str, str] = None,
                        headers: Dict[str, str] = None,
                        data: bytes = None,
                        json_data: dict = None) -> dict:
        request = dict(
            method=method,
            url=endpoint.format(**path),
            params=query
        )

        if json_data:
            request['json'] = json_data
        elif data:
            request['data'] = data

        if headers:
            request['headers'] = headers

        return request

    @staticmethod
    def to_universal_response(response: httpx.Response):
        return types.UniversalResponse(
            status_code=response.status_code,
            headers=response.headers,
            data=response.content
        )
