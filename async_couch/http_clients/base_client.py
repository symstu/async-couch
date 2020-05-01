import abc

from dataclasses import dataclass
from typing import Callable, Dict, Any

from async_couch import exc, types
from async_couch.utils.content_types import MultipartRelated


class BaseHttpClient(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def get_client(cls, url: str):
        return NotImplemented

    @abc.abstractmethod
    async def request_method(self, *_, **__) -> Callable:
        return NotImplemented

    @staticmethod
    @abc.abstractmethod
    def prepare_request(endpoint: str,
                        method: str,
                        path: Dict[str, str] = None,
                        query: Dict[str, str] = None,
                        headers: Dict[str, str] = None,
                        data: bytes = None,
                        json_data: dict = None) -> dict:
        return NotImplemented

    @staticmethod
    @abc.abstractmethod
    def to_universal_response(response: Any):
        return NotImplemented

    async def make_request(self,
                           endpoint: str,
                           method: str,
                           statuses: Dict[int, str],
                           path: Dict[str, Any] = None,
                           query: Dict[str, Any] = None,
                           headers: Dict[str, Any] = None,
                           data: bytes = None,
                           json_data: dict = None,
                           response_model: Any = None):
        func_kwargs = self.prepare_request(
            endpoint, method, path, query, headers, data, json_data)
        result = await self.request_method(**func_kwargs)

        response = self.to_universal_response(
            self.validate_response(result, statuses))
        content_type = response.headers.get('content-type')

        if response_model:
            if content_type == 'application/json':
                response.model = response_model.load(response)

            elif content_type.startswith('multipart/related'):
                decoded_attachments = list(MultipartRelated.load(response.data))
                response.model = response_model.load(decoded_attachments[0])
                response.model._files = decoded_attachments

        return response

    @staticmethod
    def validate_response(response: types.UniversalResponse, statutes: dict):
        if response.status_code > 299:
            raise exc.CouchResponseError(
                response.status_code, response.content)

        status = statutes.get(response.status_code)

        if not status:
            raise exc.UnexpectedStatusCode(
                response.status_code, response.content)

        return response


@dataclass
class BaseEndpoint:
    http_client: BaseHttpClient
