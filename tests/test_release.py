"""Tests for release-asset resource descriptors: the _cache property, hash resolution, and calver."""

import datetime
import os
import shutil
import subprocess

import frictionless
import pytest

from morpc.frictionless import (
    calver,
    create_release,
    create_resource,
    get_private_release_asset,
    load_data,
    load_package,
    parse_release_asset_url,
    prepare_release,
    publish_paths,
    release_asset_url,
    resolve_data_path,
    write_resource,
)


ASSET_URL = "https://github.com/morpc/morpc-parcels-standardize/releases/download/v2026.7.22/data.csv"

SCHEMA_YAML = """\
fields:
  - name: id
    type: integer
  - name: name
    type: string
"""


def _build_data(dirpath, name="data.csv"):
    """Write a small CSV plus its schema sidecar into dirpath. Returns the data file path."""
    dataPath = dirpath / name
    dataPath.write_bytes(b"id,name\r\n1,alice\r\n2,bob\r\n")
    (dirpath / name.replace(".csv", ".schema.yaml")).write_text(SCHEMA_YAML)
    return dataPath


# --- release_asset_url ---

def test_release_asset_url_shape():
    url = release_asset_url("morpc", "morpc-parcels-standardize", "v2026.7.22", "data.csv")
    assert url == ASSET_URL


def test_parse_release_asset_url_round_trips():
    assert parse_release_asset_url(ASSET_URL) == ("morpc", "morpc-parcels-standardize", "v2026.7.22", "data.csv")


def test_parse_release_asset_url_rejects_non_matching_url():
    assert parse_release_asset_url("https://example.com/data.csv") is None


def test_parse_release_asset_url_handles_latest_shape_with_no_tag():
    url = "https://github.com/morpc/morpc-parcels-standardize/releases/latest/download/data.csv"
    assert parse_release_asset_url(url) == ("morpc", "morpc-parcels-standardize", None, "data.csv")


# --- calver ---

def test_calver_is_unpadded_and_round_trips():
    from packaging.version import Version

    version = calver(datetime.date(2026, 7, 22))
    assert version == "2026.7.22"
    # A zero-padded version would normalize to something else, breaking the tag correspondence.
    assert str(Version(version)) == version


def test_calver_with_sequence():
    version = calver(datetime.date(2026, 7, 22), sequence=1)
    assert version == "2026.7.22.1"


def test_calver_defaults_to_today():
    today = datetime.date.today()
    assert calver() == "{}.{}.{}".format(today.year, today.month, today.day)


# --- create_resource: hash algorithm ---

def test_create_resource_default_hash_is_bare_md5(tmp_path):
    # The historical Data Package v1 form. Existing callers must be unaffected by the new defaults.
    _build_data(tmp_path)
    resource = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
    )
    assert ":" not in resource.hash
    assert len(resource.hash) == 32
    assert resource.bytes == os.path.getsize(tmp_path / "data.csv")


def test_create_resource_sha256_is_self_describing(tmp_path):
    import morpc

    dataPath = _build_data(tmp_path)
    resource = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        hashAlgorithm="sha256",
    )
    assert resource.hash == "sha256:{}".format(morpc.sha256(str(dataPath)))


def test_create_resource_unsupported_hash_algorithm_raises(tmp_path):
    _build_data(tmp_path)
    with pytest.raises(RuntimeError):
        create_resource(
            "data.csv",
            resourcePath=str(tmp_path / "data.resource.yaml"),
            ignoreSchema=True,
            hashAlgorithm="crc32",
        )


# --- create_resource: cache ---

def test_create_resource_hash_and_bytes_come_from_cache_when_path_is_url(tmp_path):
    dataPath = _build_data(tmp_path)
    local = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        hashAlgorithm="sha256",
    )
    remote = create_resource(
        ASSET_URL,
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        cache="data.csv",
        name="parcels",
        hashAlgorithm="sha256",
    )
    # The URL is not locally addressable, so the bytes are resolved through the cache. They describe
    # the same file, so the hash and size must agree with the purely local resource.
    assert remote.path == ASSET_URL
    assert remote.custom["_cache"] == "data.csv"
    assert remote.hash == local.hash
    assert remote.bytes == local.bytes == os.path.getsize(dataPath)


def test_create_resource_url_without_cache_raises(tmp_path):
    _build_data(tmp_path)
    with pytest.raises(RuntimeError):
        create_resource(
            ASSET_URL,
            resourcePath=str(tmp_path / "data.resource.yaml"),
            ignoreSchema=True,
            name="parcels",
        )


def test_create_resource_url_without_cache_is_fine_when_nothing_is_computed(tmp_path):
    # With no hash or size to compute there is nothing that needs local bytes.
    resource = create_resource(
        ASSET_URL,
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        name="parcels",
        computeHash=False,
        computeBytes=False,
    )
    assert resource.path == ASSET_URL
    assert resource.format == "csv"


def test_create_resource_cache_round_trips_through_disk(tmp_path):
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        ASSET_URL,
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        cache="data.csv",
        name="parcels",
        writeResource=True,
    )
    # _cache is a custom property, so the round trip is the thing worth asserting: frictionless must
    # preserve it through write and read rather than dropping it as unrecognized.
    reread = frictionless.Resource(str(resourcePath))
    assert reread.path == ASSET_URL
    assert reread.custom["_cache"] == "data.csv"


# --- resolve_data_path ---

def test_resolve_data_path_plain_local_resource(tmp_path):
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        "data.csv",
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        writeResource=True,
    )
    resource = frictionless.Resource(str(resourcePath))
    resolved = resolve_data_path(resource, str(tmp_path))
    assert os.path.abspath(resolved) == os.path.abspath(tmp_path / "data.csv")


def test_resolve_data_path_cache_hit_does_not_download(tmp_path, monkeypatch):
    import morpc.req

    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        ASSET_URL,
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        cache="data.csv",
        name="parcels",
        writeResource=True,
    )

    def _fail(*args, **kwargs):
        raise AssertionError("The cached copy is present, so no download should be attempted.")

    monkeypatch.setattr(morpc.req, "get_file_safely", _fail)

    resource = frictionless.Resource(str(resourcePath))
    resolved = resolve_data_path(resource, str(tmp_path))
    assert os.path.abspath(resolved) == os.path.abspath(tmp_path / "data.csv")


def test_resolve_data_path_cache_miss_downloads_to_cache(tmp_path, monkeypatch):
    import morpc.req

    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    _build_data(sourceDir)
    resourcePath = sourceDir / "data.resource.yaml"
    create_resource(
        ASSET_URL,
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        cache="data.csv",
        name="parcels",
        writeResource=True,
    )

    # Stand the data up somewhere else and remove the cached copy, so the resource describes data
    # that is not present locally.
    origin = tmp_path / "origin" / "data.csv"
    origin.parent.mkdir()
    shutil.move(str(sourceDir / "data.csv"), str(origin))

    def _fake_download(url, output_dir, returnPath=False, **kwargs):
        assert url == ASSET_URL
        target = os.path.join(output_dir, os.path.basename(url))
        shutil.copyfile(str(origin), target)
        return target

    monkeypatch.setattr(morpc.req, "get_file_safely", _fake_download)

    resource = frictionless.Resource(str(resourcePath))
    resolved = resolve_data_path(resource, str(sourceDir))
    # The download lands at the cache location, so a second call is served locally.
    assert os.path.abspath(resolved) == os.path.abspath(sourceDir / "data.csv")
    assert os.path.exists(sourceDir / "data.csv")


def test_resolve_data_path_url_without_cache_uses_temporary_directory(tmp_path, monkeypatch):
    import morpc.req

    origin = tmp_path / "origin" / "data.csv"
    origin.parent.mkdir()
    _build_data(origin.parent)

    resource = frictionless.Resource.from_descriptor({
        "name": "parcels",
        "path": ASSET_URL,
        "format": "csv",
    })

    def _fake_download(url, output_dir, returnPath=False, **kwargs):
        target = os.path.join(output_dir, os.path.basename(url))
        shutil.copyfile(str(origin), target)
        return target

    monkeypatch.setattr(morpc.req, "get_file_safely", _fake_download)

    resolved = resolve_data_path(resource, str(tmp_path))
    assert os.path.exists(resolved)
    # Nothing was written into the resource directory, since the resource named no cache.
    assert not os.path.exists(tmp_path / "data.csv")


def test_resolve_data_path_download_disabled_raises(tmp_path):
    resource = frictionless.Resource.from_descriptor({
        "name": "parcels",
        "path": ASSET_URL,
        "format": "csv",
    })
    with pytest.raises(RuntimeError):
        resolve_data_path(resource, str(tmp_path), download=False)


def test_resolve_data_path_hash_mismatch_raises(tmp_path):
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        ASSET_URL,
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        cache="data.csv",
        name="parcels",
        writeResource=True,
    )

    # The cached file no longer matches the hash the resource records for it.
    (tmp_path / "data.csv").write_bytes(b"id,name\r\n1,changed\r\n")

    resource = frictionless.Resource(str(resourcePath))
    with pytest.raises(RuntimeError):
        resolve_data_path(resource, str(tmp_path))


def test_resolve_data_path_falls_back_to_private_asset_when_token_present(tmp_path, monkeypatch):
    import requests
    import morpc.req

    origin = tmp_path / "origin" / "data.csv"
    origin.parent.mkdir()
    _build_data(origin.parent)

    resource = frictionless.Resource.from_descriptor({
        "name": "parcels",
        "path": ASSET_URL,
        "format": "csv",
    })

    def _fail_public(url, output_dir, returnPath=False, **kwargs):
        raise requests.HTTPError("404 Client Error")

    def _fake_private(url, output_dir, token, returnPath=False, **kwargs):
        assert url == ASSET_URL
        assert token == "secret-token"
        target = os.path.join(output_dir, os.path.basename(url))
        shutil.copyfile(str(origin), target)
        return target

    monkeypatch.setattr(morpc.req, "get_file_safely", _fail_public)
    monkeypatch.setattr("morpc.frictionless.release.get_private_release_asset", _fake_private)
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token")

    resolved = resolve_data_path(resource, str(tmp_path))
    assert os.path.exists(resolved)


def test_resolve_data_path_reraises_when_no_token(tmp_path, monkeypatch):
    import requests
    import morpc.req

    resource = frictionless.Resource.from_descriptor({
        "name": "parcels",
        "path": ASSET_URL,
        "format": "csv",
    })

    def _fail_public(url, output_dir, returnPath=False, **kwargs):
        raise requests.HTTPError("404 Client Error")

    monkeypatch.setattr(morpc.req, "get_file_safely", _fail_public)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(requests.HTTPError):
        resolve_data_path(resource, str(tmp_path))


# --- get_private_release_asset ---

def test_get_private_release_asset_downloads_matching_asset(tmp_path, monkeypatch):
    import requests
    import morpc.req

    _build_data(tmp_path, name="downloaded.csv")
    dataBytes = (tmp_path / "downloaded.csv").read_bytes()

    class _FakeResponse:
        def __init__(self, json_data=None, content=b""):
            self._json = json_data
            self._content = content

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

        def iter_content(self, chunk_size):
            yield self._content

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    calls = []

    def _fake_get(url, headers=None, params=None, stream=False):
        calls.append((url, headers))
        if url == "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/tags/v2026.7.22":
            return _FakeResponse(json_data={"assets": [
                {"name": "other.csv", "url": "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/assets/1"},
                {"name": "data.csv", "url": "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/assets/2"},
            ]})
        assert url == "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/assets/2"
        return _FakeResponse(content=dataBytes)

    monkeypatch.setattr(requests, "get", _fake_get)

    output_dir = tmp_path / "out"
    output_dir.mkdir()
    path = get_private_release_asset(ASSET_URL, str(output_dir), "secret-token", returnPath=True)

    assert os.path.exists(path)
    assert open(path, "rb").read() == dataBytes
    # The second call must hit the asset endpoint with the octet-stream Accept header, not the JSON one.
    assert calls[1][1]["Accept"] == "application/octet-stream"
    assert calls[1][1]["Authorization"] == "Bearer secret-token"


def test_get_private_release_asset_resolves_latest_release(tmp_path, monkeypatch):
    # A "latest" URL names no tag, so the release must be resolved via GitHub's own "get the latest
    # release" endpoint instead of the tags/{tag} one used for a pinned URL.
    import requests

    latestUrl = "https://github.com/morpc/morpc-parcels-standardize/releases/latest/download/data.csv"
    dataBytes = b"id,name\r\n1,alice\r\n"

    class _FakeResponse:
        def __init__(self, json_data=None, content=b""):
            self._json = json_data
            self._content = content

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

        def iter_content(self, chunk_size):
            yield self._content

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    calls = []

    def _fake_get(url, headers=None, params=None, stream=False):
        calls.append(url)
        if url == "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/latest":
            return _FakeResponse(json_data={"assets": [
                {"name": "data.csv", "url": "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/assets/9"},
            ]})
        assert url == "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/assets/9"
        return _FakeResponse(content=dataBytes)

    monkeypatch.setattr(requests, "get", _fake_get)

    output_dir = tmp_path / "out"
    output_dir.mkdir()
    path = get_private_release_asset(latestUrl, str(output_dir), "secret-token", returnPath=True)

    assert calls[0] == "https://api.github.com/repos/morpc/morpc-parcels-standardize/releases/latest"
    assert open(path, "rb").read() == dataBytes


def test_get_private_release_asset_missing_asset_raises(tmp_path, monkeypatch):
    import requests
    import morpc.req

    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"assets": []}

    monkeypatch.setattr(requests, "get", lambda url, headers=None, params=None, stream=False: _FakeResponse())

    with pytest.raises(RuntimeError):
        get_private_release_asset(ASSET_URL, str(tmp_path), "secret-token")


def test_get_private_release_asset_rejects_non_release_url(tmp_path):
    import morpc.req

    with pytest.raises(ValueError):
        get_private_release_asset("https://example.com/data.csv", str(tmp_path), "secret-token")


# --- load_data with a URL resourcePath ---
#
# A RELEASE_URL env var (morpc-addresspoints-geocoder's pin-then-redeploy convention) points directly
# at a released *.resource.yaml*, not at a local descriptor file -- so resourcePath itself is a URL,
# not just resource.path within it. Three distinct bugs surfaced only by exercising that shape.

def test_load_data_url_resourcepath_not_mangled_by_normpath(tmp_path, monkeypatch):
    # os.path.normpath() collapses "https://" to "https:/", which then fails to parse as a URL at
    # all. Regression test: capture what load_resource() actually receives and assert the "//" survived.
    import sys
    ff = sys.modules["morpc.frictionless.frictionless"]

    _build_data(tmp_path, name="data.csv")
    create_resource(
        "data.csv", resourcePath=str(tmp_path / "data.resource.yaml"), ignoreSchema=True,
        name="parcels", writeResource=True,
    )

    url = "https://example.org/release/data.resource.yaml"
    captured = {}
    realResource = frictionless.Resource(str(tmp_path / "data.resource.yaml"))

    def _fake_load_resource(path):
        captured["path"] = path
        return realResource

    monkeypatch.setattr(ff, "load_resource", _fake_load_resource)

    data, resource, schema = load_data(url, archiveDir=str(tmp_path), useSchema=None)

    assert captured["path"] == url
    assert "https://" in captured["path"]


def test_load_resource_falls_back_to_private_asset_for_url_descriptor(tmp_path, monkeypatch):
    # The plain descriptor fetch has no knowledge of GITHUB_TOKEN at all -- distinct from
    # resolve_data_path()'s fallback, which only covers the *data* file, not the descriptor itself.
    import frictionless as fl
    import requests

    from morpc.frictionless.frictionless import load_resource

    url = "https://github.com/morpc/morpc-parcels-standardize/releases/download/v2026.7.22/data.resource.yaml"
    _build_data(tmp_path, name="downloaded.csv")
    localResourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        "downloaded.csv", resourcePath=str(localResourcePath), ignoreSchema=True,
        name="parcels", writeResource=True,
    )

    realResourceCtor = frictionless.Resource

    def _fake_resource_ctor(path):
        if path == url:
            raise fl.FrictionlessException(fl.errors.SchemeError(note="not found")) from requests.HTTPError("404")
        return realResourceCtor(path)

    def _fake_private_asset(assetUrl, output_dir, token, returnPath=False, **kwargs):
        assert assetUrl == url
        assert token == "secret-token"
        shutil.copyfile(str(localResourcePath), os.path.join(output_dir, "data.resource.yaml"))
        return os.path.join(output_dir, "data.resource.yaml")

    monkeypatch.setattr(frictionless, "Resource", _fake_resource_ctor)
    monkeypatch.setattr("morpc.frictionless.release.get_private_release_asset", _fake_private_asset)
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token")

    resource = load_resource(url)
    assert resource.name == "parcels"


def test_load_data_url_resourcepath_resolves_directly_into_archive_dir(tmp_path, monkeypatch):
    # Regression test for a real duplicate-download bug: without special handling, sourceDir for a
    # URL resourcePath became a bogus dirname-of-URL (e.g. "./https:/example.org/release"), so
    # resolve_data_path() cached the data there instead of into archiveDir -- a second, unwanted full
    # copy on every run. Assert only archiveDir's copy exists, nothing under a URL-shaped directory.
    import sys
    ff = sys.modules["morpc.frictionless.frictionless"]

    origin = tmp_path / "origin.csv"
    _build_data(tmp_path, name="origin.csv")

    url = "https://example.org/release/data.resource.yaml"
    realResource = frictionless.Resource.from_descriptor({
        "name": "parcels",
        "path": "https://example.org/release/data.csv",
        "format": "csv",
        "_cache": "data.csv",
    })

    def _fake_load_resource(path):
        return realResource

    def _fake_download(fetchUrl, output_dir, returnPath=False, **kwargs):
        target = os.path.join(output_dir, "data.csv")
        shutil.copyfile(str(origin), target)
        return target

    monkeypatch.setattr(ff, "load_resource", _fake_load_resource)
    monkeypatch.setattr("morpc.req.get_file_safely", _fake_download)

    archiveDir = tmp_path / "archive"
    archiveDir.mkdir()
    data, resource, schema = load_data(url, archiveDir=str(archiveDir), useSchema=None)

    assert (archiveDir / "data.csv").exists()
    assert not (tmp_path / "https:").exists()
    assert not (tmp_path / "example.org").exists()


def test_resolve_data_path_verifies_sha256_hash(tmp_path):
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        ASSET_URL,
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        cache="data.csv",
        name="parcels",
        hashAlgorithm="sha256",
        writeResource=True,
    )
    resource = frictionless.Resource(str(resourcePath))
    assert resource.hash.startswith("sha256:")
    # Verification passes on the intact file and fails once the bytes change.
    resolve_data_path(resource, str(tmp_path))
    (tmp_path / "data.csv").write_bytes(b"id,name\r\n1,changed\r\n")
    with pytest.raises(RuntimeError):
        resolve_data_path(resource, str(tmp_path))


# --- publish_paths ---

def test_publish_paths_rewrites_path_and_records_cache(tmp_path):
    _build_data(tmp_path)
    local = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        name="parcels",
    )
    published = publish_paths(local, "morpc", "morpc-parcels-standardize", "v2026.7.22")

    assert published.path == ASSET_URL
    assert published.custom["_cache"] == "data.csv"
    # The hash and bytes carry over, so a consumer can verify the downloaded asset.
    assert published.hash == local.hash
    assert published.bytes == local.bytes
    # The original resource is not modified.
    assert local.path == "data.csv"
    assert "_cache" not in local.custom


def test_publish_paths_updates_the_scheme(tmp_path):
    _build_data(tmp_path)
    local = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        name="parcels",
    )
    assert local.scheme == "file"
    published = publish_paths(local, "morpc", "morpc-parcels-standardize", "v2026.7.22")
    # Frictionless preserves an explicit scheme rather than re-deriving it, so a stale "file" would
    # otherwise survive onto a descriptor whose path is a URL.
    assert published.scheme == "https"


def test_publish_paths_preserves_dialect_and_schema(tmp_path, monkeypatch):
    # A sqlite resource carries a dialect naming the table and a schema sidecar reference. Both must
    # survive the rewrite, or the published descriptor cannot open the data it points at.
    from frictionless import formats

    # A resource built in memory has no basepath, so its schema reference resolves against the working
    # directory.
    monkeypatch.chdir(tmp_path)
    _build_data(tmp_path)
    local = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        schemaPath="data.schema.yaml",
        name="parcels",
        control=formats.SqlControl(table="addresspoints"),
    )
    published = publish_paths(local, "morpc", "morpc-parcels-standardize", "v2026.7.22")
    descriptor = published.to_dict()
    assert descriptor["dialect"] == {"sql": {"table": "addresspoints"}}
    assert descriptor["schema"] == "data.schema.yaml"


def test_publish_paths_on_an_already_published_resource_retags(tmp_path):
    _build_data(tmp_path)
    local = create_resource(
        "data.csv",
        resourcePath=str(tmp_path / "data.resource.yaml"),
        ignoreSchema=True,
        name="parcels",
    )
    once = publish_paths(local, "morpc", "morpc-parcels-standardize", "v2026.7.22")
    twice = publish_paths(once, "morpc", "morpc-parcels-standardize", "v2026.8.1")

    assert twice.path.endswith("/download/v2026.8.1/data.csv")
    assert twice.custom["_cache"] == "data.csv"


def test_publish_paths_without_a_path_raises():
    resource = frictionless.Resource.from_descriptor({"name": "parcels", "data": [["id"], [1]]})
    with pytest.raises(RuntimeError):
        publish_paths(resource, "morpc", "morpc-parcels-standardize", "v2026.7.22")


# --- prepare_release ---

def test_prepare_release_rewrites_descriptors_and_creates_package(tmp_path):
    _build_data(tmp_path, name="data1.csv")
    _build_data(tmp_path, name="data2.csv")
    resource1Path = tmp_path / "data1.resource.yaml"
    resource2Path = tmp_path / "data2.resource.yaml"
    create_resource("data1.csv", resourcePath=str(resource1Path), ignoreSchema=True, name="one", writeResource=True)
    create_resource("data2.csv", resourcePath=str(resource2Path), ignoreSchema=True, name="two", writeResource=True)

    published = prepare_release(
        [str(resource1Path), str(resource2Path)],
        "morpc",
        "repo",
        "v2026.7.22",
        packageName="bundle",
    )

    assert len(published) == 2
    assert published[0].path.endswith("/download/v2026.7.22/data1.csv")
    assert published[1].path.endswith("/download/v2026.7.22/data2.csv")

    # Both descriptors were rewritten on disk, not just returned in memory.
    reread1 = frictionless.Resource(str(resource1Path))
    reread2 = frictionless.Resource(str(resource2Path))
    assert reread1.path.endswith("/download/v2026.7.22/data1.csv")
    assert reread1.custom["_cache"] == "data1.csv"
    assert reread2.path.endswith("/download/v2026.7.22/data2.csv")
    assert reread2.custom["_cache"] == "data2.csv"

    # The package descriptor must round-trip through frictionless.Package() itself, which requires
    # each resource to be an inline object rather than a bare path string.
    package = frictionless.Package(str(tmp_path / "bundle.package.yaml"))
    assert package.version == "2026.7.22"
    assert [r.name for r in package.resources] == ["one", "two"]
    assert package.resources[0].path.endswith("/download/v2026.7.22/data1.csv")
    assert package.resources[1].path.endswith("/download/v2026.7.22/data2.csv")


def test_prepare_release_accepts_a_bare_string_path(tmp_path):
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)

    published = prepare_release(str(resourcePath), "morpc", "repo", "v2026.7.22")

    assert len(published) == 1
    assert published[0].path.endswith("/download/v2026.7.22/data.csv")


# --- create_release ---

class _FakeCompleted:
    def __init__(self, returncode):
        self.returncode = returncode


def _build_shared_schema_resources(tmp_path):
    """Two resources whose schema attribute both point at the same schema sidecar file."""
    (tmp_path / "shared.schema.yaml").write_text(SCHEMA_YAML)
    for name in ("data1.csv", "data2.csv"):
        (tmp_path / name).write_bytes(b"id,name\r\n1,alice\r\n2,bob\r\n")

    resource1Path = tmp_path / "data1.resource.yaml"
    resource2Path = tmp_path / "data2.resource.yaml"
    create_resource(
        "data1.csv", resourcePath=str(resource1Path), schemaPath="shared.schema.yaml", name="one", writeResource=True
    )
    create_resource(
        "data2.csv", resourcePath=str(resource2Path), schemaPath="shared.schema.yaml", name="two", writeResource=True
    )
    return str(resource1Path), str(resource2Path)


def test_create_release_dedupes_a_schema_shared_by_two_resources(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    resource1Path, resource2Path = _build_shared_schema_resources(tmp_path)

    assets, notes = create_release([resource1Path, resource2Path], "morpc", "repo", "v2026.7.22", dryRun=True)

    absAssets = [os.path.abspath(asset) for asset in assets]
    assert len(absAssets) == len(set(absAssets))
    assert absAssets.count(os.path.abspath(tmp_path / "shared.schema.yaml")) == 1
    assert os.path.abspath(tmp_path / "data1.csv") in absAssets
    assert os.path.abspath(tmp_path / "data2.csv") in absAssets
    assert os.path.abspath(resource1Path) in absAssets
    assert os.path.abspath(resource2Path) in absAssets


def test_create_release_resolves_published_data_through_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    local = create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels")
    published = publish_paths(local, "morpc", "morpc-parcels-standardize", "v2026.7.22")
    write_resource(published, str(resourcePath))

    assets, notes = create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22", dryRun=True)

    absAssets = [os.path.abspath(asset) for asset in assets]
    # The data asset resolves through _cache, not the release asset URL, which is not a local path.
    assert os.path.abspath(tmp_path / "data.csv") in absAssets


def test_create_release_url_path_without_cache_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    resourcePath = tmp_path / "data.resource.yaml"
    resource = frictionless.Resource.from_descriptor({"name": "parcels", "path": ASSET_URL, "format": "csv"})
    write_resource(resource, str(resourcePath))

    with pytest.raises(RuntimeError):
        create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22", dryRun=True)


def test_create_release_appends_extra_assets(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)
    extraPath = tmp_path / "bundle.package.yaml"
    extraPath.write_text("name: bundle\n")

    assets, notes = create_release(
        [str(resourcePath)], "morpc", "repo", "v2026.7.22", assets=[str(extraPath)], dryRun=True
    )

    assert os.path.abspath(extraPath) in [os.path.abspath(asset) for asset in assets]


def test_create_release_notes_include_resource_details_and_intro(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        "data.csv",
        resourcePath=str(resourcePath),
        ignoreSchema=True,
        name="parcels",
        title="Parcels",
        description="County parcel data.",
        writeResource=True,
    )

    assets, notes = create_release(
        [str(resourcePath)], "morpc", "repo", "v2026.7.22", notes="Intro text.", dryRun=True
    )

    assert "Intro text." in notes
    assert "Parcels" in notes
    assert "`parcels`" in notes
    assert "County parcel data." in notes
    dataBytes = os.path.getsize(tmp_path / "data.csv")
    assert "{:,} bytes".format(dataBytes) in notes
    resource = frictionless.Resource(str(resourcePath))
    assert resource.hash in notes


def test_create_release_missing_asset_raises_before_any_gh_call(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)
    os.remove(tmp_path / "data.csv")

    def _fail(*args, **kwargs):
        raise AssertionError("gh should not be invoked when an asset is missing.")

    monkeypatch.setattr(subprocess, "run", _fail)

    with pytest.raises(RuntimeError):
        create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22")


def test_create_release_existing_tag_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)

    def _fake_run(args, **kwargs):
        assert args[:3] == ["gh", "release", "view"]
        return _FakeCompleted(0)

    monkeypatch.setattr(subprocess, "run", _fake_run)

    with pytest.raises(RuntimeError):
        create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22")


def test_create_release_invokes_gh_with_the_expected_arguments(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)

    calls = []

    def _fake_run(args, **kwargs):
        calls.append(args)
        # A non-zero return from the tag check means no such release, so the create proceeds.
        return _FakeCompleted(1)

    monkeypatch.setattr(subprocess, "run", _fake_run)

    assets, notes = create_release(
        [str(resourcePath)], "morpc", "repo", "v2026.7.22", title="2026.7.22", notes="Intro text."
    )

    view, create = calls
    assert view == ["gh", "release", "view", "v2026.7.22", "--repo", "morpc/repo"]
    assert create[:6] == ["gh", "release", "create", "v2026.7.22", "--repo", "morpc/repo"]
    assert create[6:10] == ["--title", "2026.7.22", "--notes", notes]
    # Every derived asset is passed positionally after the flags, in order.
    assert create[10:] == assets


def test_create_release_title_defaults_to_the_tag(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)

    calls = []

    def _fake_run(args, **kwargs):
        calls.append(args)
        return _FakeCompleted(1)

    monkeypatch.setattr(subprocess, "run", _fake_run)

    create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22")

    create = calls[1]
    assert create[create.index("--title") + 1] == "v2026.7.22"


def test_create_release_missing_gh_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)

    with pytest.raises(RuntimeError):
        create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22")


def test_prepare_release_bare_filename_packages_into_the_working_directory(tmp_path, monkeypatch):
    # A descriptor named without a directory has no dirname, so the package directory falls back to ".".
    monkeypatch.chdir(tmp_path)
    _build_data(tmp_path)
    create_resource("data.csv", resourcePath="data.resource.yaml", ignoreSchema=True, name="parcels", writeResource=True)

    prepare_release("data.resource.yaml", "morpc", "repo", "v2026.7.22", packageName="bundle")

    assert os.path.exists(tmp_path / "bundle.package.yaml")


def test_prepare_release_descriptors_in_different_directories_raise(tmp_path):
    first = tmp_path / "a"
    second = tmp_path / "b"
    first.mkdir()
    second.mkdir()
    _build_data(first)
    _build_data(second)
    create_resource("data.csv", resourcePath=str(first / "data.resource.yaml"), ignoreSchema=True, name="one", writeResource=True)
    create_resource("data.csv", resourcePath=str(second / "data.resource.yaml"), ignoreSchema=True, name="two", writeResource=True)

    with pytest.raises(RuntimeError):
        prepare_release(
            [str(first / "data.resource.yaml"), str(second / "data.resource.yaml")],
            "morpc",
            "repo",
            "v2026.7.22",
            packageName="bundle",
        )


def test_create_release_dry_run_skips_tag_check_and_create(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gh")
    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource("data.csv", resourcePath=str(resourcePath), ignoreSchema=True, name="parcels", writeResource=True)

    def _fail(*args, **kwargs):
        raise AssertionError("A dry run must not invoke gh at all.")

    monkeypatch.setattr(subprocess, "run", _fail)

    assets, notes = create_release([str(resourcePath)], "morpc", "repo", "v2026.7.22", dryRun=True)

    assert len(assets) == 2  # the data file and the descriptor


# --- load_data ---

def test_load_data_reads_through_the_cache(tmp_path, monkeypatch):
    import morpc.req
    from morpc.frictionless import load_data

    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        ASSET_URL,
        resourcePath=str(resourcePath),
        schemaPath="data.schema.yaml",
        cache="data.csv",
        name="parcels",
        writeResource=True,
    )

    def _fail(*args, **kwargs):
        raise AssertionError("The cached copy is present, so no download should be attempted.")

    monkeypatch.setattr(morpc.req, "get_file_safely", _fail)

    data, resource, schema = load_data(str(resourcePath))
    assert list(data.columns) == ["id", "name"]
    assert data["name"].tolist() == ["alice", "bob"]


def test_load_data_local_resource_is_unaffected(tmp_path):
    from morpc.frictionless import load_data

    _build_data(tmp_path)
    resourcePath = tmp_path / "data.resource.yaml"
    create_resource(
        "data.csv",
        resourcePath=str(resourcePath),
        schemaPath="data.schema.yaml",
        name="parcels",
        writeResource=True,
    )
    data, resource, schema = load_data(str(resourcePath))
    assert data["id"].tolist() == [1, 2]
