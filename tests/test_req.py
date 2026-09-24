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


# Census and ArcGIS requests carry credentials as query parameters (key=, token=). Logs and exception
# messages end up in committed notebook outputs, so they must never contain them.

SECRET = "s3cr3t-api-key"
SECRET_URL = f"http://example/data?get=NAME&key={SECRET}"


class _SecretResponse(_Response):
    def __init__(self, status_code, payload=None):
        super().__init__(status_code, payload)
        self.url = SECRET_URL

    def raise_for_status(self):
        # Mirrors requests: the message includes the full URL.
        if self.status_code != 200:
            raise HTTPError(f"{self.status_code} Client Error: Not Found for url: {self.url}", response=self)

    def iter_content(self, chunk_size=1):
        return iter([b"data"])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _SecretSession(_FakeSession):
    def get(self, url, params=None, headers=None, stream=False):
        return self._response


def _assert_no_secret(caplog, excinfo=None):
    assert SECRET not in caplog.text
    if excinfo is not None:
        assert SECRET not in str(excinfo.value)


@pytest.mark.parametrize("status", [204, 400, 404])
def test_get_json_safely_failure_does_not_leak_key(caplog, status):
    caplog.set_level("DEBUG")
    with pytest.raises(HTTPError) as excinfo:
        get_json_safely("http://example/data", params={"key": SECRET}, session=_SecretSession(_SecretResponse(status)))
    _assert_no_secret(caplog, excinfo)


def test_get_json_safely_success_does_not_leak_key(caplog):
    caplog.set_level("DEBUG")
    get_json_safely("http://example/data", params={"key": SECRET}, session=_SecretSession(_SecretResponse(200, [["a"]])))
    _assert_no_secret(caplog)


def test_get_json_safely_decode_error_does_not_leak_key(caplog):
    class _BadJSON(_SecretResponse):
        def json(self):
            raise ValueError("not json")
    caplog.set_level("DEBUG")
    with pytest.raises(Exception) as excinfo:
        get_json_safely(SECRET_URL, session=_SecretSession(_BadJSON(200)))
    _assert_no_secret(caplog, excinfo)


def test_get_text_safely_failure_does_not_leak_key(caplog):
    from morpc.req import get_text_safely
    caplog.set_level("DEBUG")
    with pytest.raises(HTTPError) as excinfo:
        get_text_safely(SECRET_URL, session=_SecretSession(_SecretResponse(400)))
    _assert_no_secret(caplog, excinfo)


def test_get_file_safely_failure_does_not_leak_key(caplog, tmp_path):
    from morpc.req import get_file_safely
    caplog.set_level("DEBUG")
    with pytest.raises(HTTPError) as excinfo:
        get_file_safely("http://example/data.csv", tmp_path, params={"token": SECRET}, session=_SecretSession(_SecretResponse(404)))
    _assert_no_secret(caplog, excinfo)


def test_redact_hides_credentials_in_urls_and_params():
    from morpc.req import redact
    assert SECRET not in redact(f"http://x/y?a=1&KEY={SECRET}&token={SECRET}&api_key={SECRET}")
    assert redact(f"http://x/y?a=1&key={SECRET}") == "http://x/y?a=1&key=REDACTED"
    assert redact({"get": "NAME", "key": SECRET}) == {"get": "NAME", "key": "REDACTED"}
    assert redact(None) is None


def test_urllib3_debug_request_log_is_redacted(caplog):
    # urllib3 logs every request line, including the query string, at DEBUG. Mirror its call.
    import logging
    import morpc.req  # noqa: F401  (installs the filter)
    caplog.set_level("DEBUG")
    logging.getLogger("urllib3.connectionpool").debug(
        '%s://%s:%s "%s %s %s" %s %s', "https", "api.census.gov", 443, "GET", f"/data/2024/acs/acs5?get=NAME&key={SECRET}", "HTTP/1.1", 200, None
    )
    assert "api.census.gov" in caplog.text
    assert "key=REDACTED" in caplog.text
    assert SECRET not in caplog.text
