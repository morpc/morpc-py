"""Tests for release-asset resource descriptors: the _cache property, hash resolution, and calver."""

import datetime
import os
import shutil

import frictionless
import pytest

from morpc.frictionless import (
    calver,
    create_resource,
    publish_paths,
    release_asset_url,
    resolve_data_path,
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
