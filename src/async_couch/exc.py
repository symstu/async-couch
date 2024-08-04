import dataclasses


@dataclasses.dataclass
class HttpError(Exception):
    """
    Base Http Error
    """

    code: int
    message: bytes


class UnexpectedStatusCode(HttpError):
    def __str__(self):
        return f"Unexpected status code {self.code} with message:" f" {self.message}"
