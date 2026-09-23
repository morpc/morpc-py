import pytest
from requests import HTTPError, Session

from morpc.req import get_json_safely


class _Response:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.text = "error"
        self.content = b"error"
        self.url = "http://example"
        self._payload = payload

    def json(self):
        return self._payload


class _FakeSession(Session):
    def __init__(self, response):
        super().__init__()
        self._response = response

    def get(self, url, params=None, headers=None):
        return self._response


def test_get_json_safely_raises_http_error_on_failed_request():
    # A non-200, non-500 response used to fall through to `return json` with json unassigned,
    # surfacing as an UnboundLocalError that hid the real HTTP failure.
    with pytest.raises(HTTPError):
        get_json_safely("http://example", session=_FakeSession(_Response(400)))


def test_get_json_safely_http_error_carries_response():
    # Callers can tell "no content" (204, e.g. a Census geography with no data for a year) from a failure.
    with pytest.raises(HTTPError) as excinfo:
        get_json_safely("http://example", session=_FakeSession(_Response(204)))
    assert excinfo.value.response.status_code == 204


def test_get_json_safely_returns_json_on_success():
    assert get_json_safely("http://example", session=_FakeSession(_Response(200, [["a"], ["1"]]))) == [["a"], ["1"]]
