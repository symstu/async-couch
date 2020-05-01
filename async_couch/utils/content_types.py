import json
import re
import gzip
import typing

from dataclasses import dataclass


new_line = b'\r\n'

multipart_boundary = b'--XFKYLGSHYCAFWJGY'


@dataclass
class MultipartRelatedAttachment:
    """
    Part of content body
    """

    mime_type: bytes = None
    """Type of content. First part always is json"""

    name: bytes = None
    """Name of attachment. For first part it's empty"""

    encoding: bytes = None
    """Content encoding"""

    data: bytes = None
    """Binary content"""

    decoding_callbacks = {
        b'gzip': gzip.decompress
    }
    """Callbacks for data decoding"""

    def decode(self) -> bytes:
        """
        Decode content with specified callbacks or rise error

        Returns
        ----------
        bytes
            decoded data

        Raises
        ----------
        Exception
            If data encoder is undefined, currently supported only gzip
        """
        if not self.encoding:
            return self.data

        encoder = self.decoding_callbacks.get(self.encoding)

        if not encoder:
            raise Exception(f'Unknown mime type : {self.mime_type}')

        return encoder(self.data)

    def encode(self) -> bytes:
        """
        Convert MultipartRelatedAttachment into request body part

        Returns
        ---------
        bytes
            Encoded part of request body
        """
        if self.mime_type == b'application/json':
            return b''.join([
                new_line, multipart_boundary,
                new_line, b'Content-Type: ', self.mime_type,
                new_line,
                new_line, self.data
            ])

        return b''.join([
            new_line, multipart_boundary,
            new_line, b'Content-Disposition: attachment; filename="', self.name, b'"',
            new_line, b'Content-Type: ', self.mime_type,
            new_line, b'Content-Length: ', str(len(self.data)).encode(),
            new_line,
            new_line, self.data
        ])

    @property
    def as_dict(self) -> dict:
        """
        Dictionary representation of Attachment. Used for _attachment attribute
        of CouchDb response

        Returns
        ---------
        dict
            Short attachment description
        """
        return dict(
            follows=True,
            content_type=self.mime_type.decode(),
            length=len(self.data)
        )

    def json(self) -> dict:
        """
        Convert data into dictionary if possible

        Returns
        ----------
        dict
            Json loaded data
        """
        return json.loads(self.data)


class MultipartRelated:
    """
    CouchDb MultipartRelated Content-Type. Parse and made request body
    """
    pattern = re.compile(b'\\n(?P<name>[\w-]*?):\s(?P<value>.*?)'
                         b'\\r|\\n\\r\\n(?P<content>.*?)\\r\\n')
    # Parse request body

    pattern_filename = re.compile(b'.*filename=\"(.*)\"')
    # Find name of attachment in Content-Disposition header

    @classmethod
    def load(cls, data: bytes) -> typing.List[MultipartRelatedAttachment]:
        """
        Parse binary data

        Parameters
        ----------
        data: bytes
            Request body

        Returns
        ----------
        typing.List[MultipartRelatedAttachment]
            List of parsed attachments
        """
        result = re.findall(cls.pattern, data)
        multipart_related_obj = MultipartRelatedAttachment()

        for header_name, header_value, content in result:
            if header_name == b'Content-Type':
                multipart_related_obj.mime_type = header_value

            elif header_name == b'Content-Disposition':
                name = re.findall(cls.pattern_filename, header_value)[0]
                multipart_related_obj.name = name

            elif header_name == b'Content-Encoding':
                multipart_related_obj.encoding = header_value

            elif content:
                multipart_related_obj.data = content
                yield multipart_related_obj
                multipart_related_obj = MultipartRelatedAttachment()

    @classmethod
    def dump(cls, attachments=typing.List[MultipartRelatedAttachment]) -> bytes:
        """
        Made http request/response body from attachments

        Parameters
        ----------
        attachments: typing.List[MultipartRelatedAttachment]
            List of attachments to encode

        Returns
        ----------
        bytes
            Bytes of encoded attachments
        """
        result = b''.join(list(map(lambda x: x.encode(), attachments)))
        return result + new_line + multipart_boundary + b'--'
