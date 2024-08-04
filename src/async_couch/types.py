try:
    import orjson as json
except ImportError:
    import json
import enum

from dataclasses import dataclass
from typing import Dict, Iterable


class HttpMethod(enum.StrEnum):
    HEAD: str = "head"
    GET: str = "get"
    POST: str = "post"
    PUT: str = "put"
    PATCH: str = "patch"
    DELETE: str = "delete"
    COPY: str = "copy"


@dataclass
class UniversalResponse:
    status_code: int
    headers: Dict[str, str]
    data: Iterable
    model: dict = None

    def json(self) -> dict:
        return json.loads(self.data)


class EmptyResponse:
    @classmethod
    def load(cls, response: UniversalResponse):
        if not response.data:
            return response

        return cls(**json.loads(response.data))


@dataclass
class CouchDbError(EmptyResponse):
    error: str
    reason: str
