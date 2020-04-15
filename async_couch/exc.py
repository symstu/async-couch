import dataclasses


@dataclasses.dataclass
class CouchResponseError(Exception):
    """

    """
    code: int
    message: bytes

    def __str__(self):
        return f'CouchDb response code {self.code}: {self.message}'


class UnexpectedStatusCode(CouchResponseError):
    def __str__(self):
        return f'Unexpected status code {self.code} with message:' \
               f' {self.message}'
