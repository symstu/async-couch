from async_couch.utils.content_types import MultipartRelated, \
    MultipartRelatedAttachment


encoded_data = b"\r\n--XFKYLGSHYCAFWJGY" \
               b"\r\nContent-Type: application/json" \
               b"\r\n" \
               b"\r\n{}" \
               b"\r\n--XFKYLGSHYCAFWJGY" \
               b"\r\nContent-Disposition: attachment; filename=\"text.txt\"" \
               b"\r\nContent-Type: text/plain" \
               b"\r\nContent-Length: 14" \
               b"\r\n" \
               b"\r\nsome test text" \
               b"\r\n--XFKYLGSHYCAFWJGY--"


def test_multipart_encoding():
    test_text = b'some test text'

    attachments = []
    attachments.append(MultipartRelatedAttachment(
        mime_type=b'application/json',
        data=b'{}'
    ))
    attachments.append(MultipartRelatedAttachment(
        mime_type=b'text/plain',
        name=b'text.txt',
        data=test_text
    ))

    assert MultipartRelated.dump(attachments) == encoded_data


def test_multipart_decoding():
    attachments = list(MultipartRelated.load(encoded_data))
    assert attachments
    assert attachments[0].decode() == b'{}'
    assert attachments[0].mime_type == b'application/json'

    assert attachments[1].decode() == b'some test text'
    assert attachments[1].name == b'text.txt'
    assert attachments[1].mime_type == b'text/plain'
