import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from morpc.frictionless import create_gpkgresource, create_package, load_data, load_package, load_resource, validate_resource
from morpc.frictionless.gpkg import GpkgControl, GpkgResource
from morpc.frictionless.release import prepare_release


POINTS_SCHEMA_YAML = """\
fields:
  - name: addr_id
    type: integer
  - name: housenum
    type: string
"""

RANGES_SCHEMA_YAML = """\
fields:
  - name: range_id
    type: integer
"""


@pytest.fixture(autouse=True)
def _chdir_tmp_path(tmp_path, monkeypatch):
    # Frictionless rejects absolute/unsafe paths in resource descriptors, so every test
    # here works with relative paths from a cwd of tmp_path, matching the convention
    # documented in create_resource(): dataPath is relative to the resource file.
    monkeypatch.chdir(tmp_path)


def _build_gpkg():
    """Two-layer GeoPackage plus hand-written schema sidecars in the current directory."""
    points = gpd.GeoDataFrame(
        {"addr_id": [1, 2], "housenum": ["100", "102"]},
        geometry=[Point(-83, 40), Point(-83.1, 40.1)],
        crs="epsg:4326",
    )
    points.to_file("addresspoints.gpkg", layer="points", driver="GPKG")

    ranges = gpd.GeoDataFrame({"range_id": [1]}, geometry=[Point(-83, 40)], crs="epsg:4326")
    ranges.to_file("addresspoints.gpkg", layer="ranges", driver="GPKG")

    with open("points.schema.yaml", "w") as f:
        f.write(POINTS_SCHEMA_YAML)
    with open("ranges.schema.yaml", "w") as f:
        f.write(RANGES_SCHEMA_YAML)


def test_create_gpkgresource_one_per_layer():
    _build_gpkg()
    resources = create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths=["points.schema.yaml", "ranges.schema.yaml"],
    )
    assert [r.name for r in resources] == ["addresspoints-points", "addresspoints-ranges"]
    assert all(r.type == "gpkg" for r in resources)
    assert all(r.path == "addresspoints.gpkg" for r in resources)
    assert GpkgControl.from_dialect(resources[0].dialect).layer == "points"
    assert GpkgControl.from_dialect(resources[1].dialect).layer == "ranges"


def test_create_gpkgresource_uppercase_layer_name_produces_valid_resource_name():
    # Frictionless resource names must match ^([-a-z0-9._/])+$. MORPC layer names are
    # conventionally uppercase (e.g. "COUNTY"), so the layer name must be lowercased when
    # building the resource name, distinct from GpkgControl.layer which must preserve the
    # original case to address the layer in the GeoPackage.
    points = gpd.GeoDataFrame(
        {"addr_id": [1]}, geometry=[Point(-83, 40)], crs="epsg:4326"
    )
    points.to_file("addresspoints.gpkg", layer="POINTS", driver="GPKG")
    with open("points.schema.yaml", "w") as f:
        f.write(POINTS_SCHEMA_YAML)

    resources = create_gpkgresource(
        "addresspoints.gpkg", layerNames=["POINTS"], schemaPaths=["points.schema.yaml"]
    )
    assert resources[0].name == "addresspoints-points"
    assert GpkgControl.from_dialect(resources[0].dialect).layer == "POINTS"


def test_create_gpkgresource_single_schema_applies_to_all_layers():
    _build_gpkg()
    resources = create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths="points.schema.yaml",
    )
    assert resources[0].schema.field_names == ["addr_id", "housenum"]
    assert resources[1].schema.field_names == ["addr_id", "housenum"]


def test_create_gpkgresource_mismatched_schema_list_length_raises():
    _build_gpkg()
    with pytest.raises(RuntimeError):
        create_gpkgresource(
            "addresspoints.gpkg",
            layerNames=["points", "ranges"],
            schemaPaths=["points.schema.yaml"],
        )


def test_create_gpkgresource_no_schema_paths():
    _build_gpkg()
    resources = create_gpkgresource("addresspoints.gpkg", layerNames=["points", "ranges"])
    assert all(len(r.schema.fields) == 0 for r in resources)


def test_gpkgresource_validate_passes():
    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths=["points.schema.yaml", "ranges.schema.yaml"],
        resourceDir=".",
        writeResource=True,
    )
    assert validate_resource("addresspoints-points.resource.yaml")
    assert validate_resource("addresspoints-ranges.resource.yaml")


def test_gpkgresource_validate_detects_schema_mismatch():
    _build_gpkg()
    with open("wrong.schema.yaml", "w") as f:
        f.write("fields:\n  - name: does_not_exist\n    type: string\n")
    resources = create_gpkgresource(
        "addresspoints.gpkg", layerNames=["points"], schemaPaths=["wrong.schema.yaml"]
    )
    report = resources[0].validate()
    assert not report.valid
    assert "does_not_exist" in report.errors[0]
    assert "not present in layer" in report.errors[0]


def test_gpkgresource_validate_detects_geometry_and_crs_mismatch():
    _build_gpkg()
    resources = create_gpkgresource(
        "addresspoints.gpkg", layerNames=["points"], schemaPaths=["points.schema.yaml"]
    )
    report = resources[0].validate(expectedGeometryType="LineString", expectedCRS="epsg:2913")
    assert not report.valid
    assert any("CRS" in e for e in report.errors)
    assert any("geometry type" in e for e in report.errors)


def test_gpkgresource_validate_detects_null_and_duplicate_geometry():
    gdf = gpd.GeoDataFrame(
        {"addr_id": [1, 2, 3], "housenum": ["100", "100", "100"]},
        geometry=[Point(-83, 40), Point(-83, 40), None],
        crs="epsg:4326",
    )
    gdf.to_file("dupes.gpkg", layer="points", driver="GPKG")
    with open("points.schema.yaml", "w") as f:
        f.write(POINTS_SCHEMA_YAML)

    resources = create_gpkgresource("dupes.gpkg", layerNames=["points"], schemaPaths=["points.schema.yaml"])
    report = resources[0].validate()
    assert not report.valid
    assert any("duplicate geometry" in e for e in report.errors)
    assert any("null or empty geometry" in e for e in report.errors)


def test_gpkgresource_validate_detects_invalid_geometry():
    # A self-intersecting "bowtie" polygon is a classic invalid geometry.
    bowtie = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])
    gdf = gpd.GeoDataFrame({"range_id": [1]}, geometry=[bowtie], crs="epsg:4326")
    gdf.to_file("bowtie.gpkg", layer="ranges", driver="GPKG")
    with open("ranges.schema.yaml", "w") as f:
        f.write(RANGES_SCHEMA_YAML)

    resources = create_gpkgresource("bowtie.gpkg", layerNames=["ranges"], schemaPaths=["ranges.schema.yaml"])
    report = resources[0].validate()
    assert not report.valid
    assert any("invalid geometry" in e for e in report.errors)


def test_load_data_uses_layer_from_control():
    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points"],
        schemaPaths=["points.schema.yaml"],
        resourceDir=".",
        writeResource=True,
    )
    data, resource, schema = load_data("addresspoints-points.resource.yaml")
    assert sorted(data["housenum"].tolist()) == ["100", "102"]


def test_create_package_bundles_multiple_layers_of_one_gpkg(tmp_path):
    # Two GpkgResources sharing a single physical .gpkg file (different `layer`, same `path`) should
    # bundle into one Package like any other pair of resources -- create_package() just loads each
    # resource file independently and doesn't assume a 1:1 file:resource mapping.
    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths=["points.schema.yaml", "ranges.schema.yaml"],
        resourceDir=".",
        writeResource=True,
    )

    package = create_package(
        dir=str(tmp_path),
        resources=["addresspoints-points.resource.yaml", "addresspoints-ranges.resource.yaml"],
        name="addresspoints",
        version="1.0.0",
    )

    assert [r.name for r in package.resources] == ["addresspoints-points", "addresspoints-ranges"]
    assert all(r.path == "addresspoints.gpkg" for r in package.resources)
    assert (tmp_path / "addresspoints.package.yaml").exists()

    for resource in package.resources:
        report = resource.validate()
        assert report.valid, report.errors


# --- load_package ---

def _build_gpkg_package(tmp_path, name="addresspoints"):
    """Two-layer local package, the shape create_package() now writes (inline resources)."""
    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths=["points.schema.yaml", "ranges.schema.yaml"],
        resourceDir=".",
        writeResource=True,
    )
    create_package(
        dir=".",
        resources=["addresspoints-points.resource.yaml", "addresspoints-ranges.resource.yaml"],
        name=name,
        version="1.0.0",
    )
    return f"{name}.package.yaml"


def test_load_package_loads_every_resource_by_default(tmp_path):
    packagePath = _build_gpkg_package(tmp_path)
    results = load_package(packagePath)

    assert set(results) == {"addresspoints-points", "addresspoints-ranges"}
    pointsData, pointsResource, pointsSchema = results["addresspoints-points"]
    assert sorted(pointsData["housenum"].tolist()) == ["100", "102"]
    assert pointsResource.name == "addresspoints-points"
    assert pointsSchema.field_names == ["addr_id", "housenum"]


def test_load_package_mixed_formats(tmp_path):
    # A package's resources don't need to share a format -- a GPKG layer and a plain CSV can sit in
    # the same package, and each should dispatch to the right loader on its own.
    import pandas as pd

    from morpc.frictionless import create_resource

    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg", layerNames=["points"], schemaPaths=["points.schema.yaml"],
        resourceDir=".", writeResource=True,
    )
    pd.DataFrame({"county": ["Franklin", "Delaware"], "count": [10, 20]}).to_csv("summary.csv", index=False)
    with open("summary.schema.yaml", "w") as f:
        f.write("fields:\n  - name: county\n    type: string\n  - name: count\n    type: integer\n")
    create_resource(
        "summary.csv", resourcePath="summary.resource.yaml", schemaPath="summary.schema.yaml",
        name="summary", writeResource=True,
    )
    create_package(
        dir=".", resources=["addresspoints-points.resource.yaml", "summary.resource.yaml"],
        name="mixed", version="1.0.0",
    )

    results = load_package("mixed.package.yaml")

    assert set(results) == {"addresspoints-points", "summary"}
    pointsData = results["addresspoints-points"][0]
    assert "geometry" in pointsData.columns
    summaryData = results["summary"][0]
    assert summaryData["count"].tolist() == [10, 20]


def test_load_package_local_package_with_separate_archive_dir(tmp_path):
    # A local (not-yet-released) package's resource paths are relative to the package's own
    # directory, not to an archiveDir the caller points somewhere else -- and frictionless refuses to
    # accept an absolute path in a descriptor ("is not safe"), so this only works if the underlying
    # data is actually copied into archiveDir rather than just referenced by a rewritten path.
    packagePath = _build_gpkg_package(tmp_path)
    cacheDir = str(tmp_path / "cache")

    results = load_package(packagePath, archiveDir=cacheDir)

    assert set(results) == {"addresspoints-points", "addresspoints-ranges"}
    assert sorted(results["addresspoints-points"][0]["housenum"].tolist()) == ["100", "102"]
    assert (tmp_path / "cache" / "addresspoints.gpkg").exists()


def test_load_package_filters_by_resource_name(tmp_path):
    packagePath = _build_gpkg_package(tmp_path)
    results = load_package(packagePath, resources="addresspoints-points")

    assert set(results) == {"addresspoints-points"}


def test_load_package_unknown_resource_name_raises(tmp_path):
    packagePath = _build_gpkg_package(tmp_path)
    with pytest.raises(RuntimeError):
        load_package(packagePath, resources=["does-not-exist"])


def test_load_package_url_without_archive_dir_raises():
    with pytest.raises(RuntimeError):
        load_package("https://example.org/bundle.package.yaml")


def test_load_package_fetches_shared_data_file_once(tmp_path, monkeypatch):
    # Both layers point at the same underlying .gpkg once published as a release. Loading both
    # resources should download that file exactly once, not once per resource.
    import shutil

    import morpc.req

    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths=["points.schema.yaml", "ranges.schema.yaml"],
        resourceDir=".",
        writeResource=True,
    )
    prepare_release(
        ["addresspoints-points.resource.yaml", "addresspoints-ranges.resource.yaml"],
        "morpc",
        "addresspoints-standardize",
        "v2026.7.30",
        packageName="addresspoints",
    )

    origin = tmp_path / "origin.gpkg"
    shutil.copyfile("addresspoints.gpkg", str(origin))

    calls = []

    def _fake_download(url, output_dir, returnPath=False, **kwargs):
        calls.append(url)
        target = f"{output_dir}/addresspoints.gpkg"
        shutil.copyfile(str(origin), target)
        return target

    monkeypatch.setattr(morpc.req, "get_file_safely", _fake_download)

    cacheDir = str(tmp_path / "cache")
    results = load_package("addresspoints.package.yaml", archiveDir=cacheDir)

    assert len(calls) == 1
    assert set(results) == {"addresspoints-points", "addresspoints-ranges"}
    assert sorted(results["addresspoints-points"][0]["housenum"].tolist()) == ["100", "102"]


def test_load_package_falls_back_to_private_asset_for_url_package(tmp_path, monkeypatch):
    # The plain package fetch has no knowledge of GITHUB_TOKEN either -- same gap as
    # load_resource(), one level up. Each selected resource's schema is also a bare sibling
    # filename reference and must be fetched too, not just the package.yaml itself.
    import os
    import shutil

    import morpc.req
    import requests

    _build_gpkg()
    create_gpkgresource(
        "addresspoints.gpkg",
        layerNames=["points", "ranges"],
        schemaPaths=["points.schema.yaml", "ranges.schema.yaml"],
        resourceDir=".",
        writeResource=True,
    )
    # prepare_release() rewrites each resource's path to a real release-asset URL, the shape a
    # published private repo's resources actually have -- without it, resource.path stays a bare
    # local filename and resolve_data_path() never exercises its own URL/private-asset handling.
    prepare_release(
        ["addresspoints-points.resource.yaml", "addresspoints-ranges.resource.yaml"],
        "morpc", "parcels-standardize", "v2026.7.22", packageName="addresspoints",
    )

    packageUrl = "https://github.com/morpc/parcels-standardize/releases/download/v2026.7.22/addresspoints.package.yaml"

    # Patched at the HTTP layer rather than replacing frictionless.Package() itself: Package's
    # class-selection machinery (unlike Resource's) breaks when the top-level name it's invoked
    # through is swapped out for a plain function mid-call. This way the real frictionless code runs
    # throughout and only the one request actually fails.
    from frictionless import platform
    session = platform.frictionless.system.http_session
    realGet = session.get

    class _FakeResponse:
        def raise_for_status(self):
            raise requests.HTTPError("404", response=self)

    def _fake_get(requestUrl, *args, **kwargs):
        if requestUrl == packageUrl:
            return _FakeResponse()
        return realGet(requestUrl, *args, **kwargs)

    def _fake_get_file_safely(dataUrl, output_dir, returnPath=False, **kwargs):
        raise requests.HTTPError("404 Client Error")

    def _fake_private_asset(assetUrl, output_dir, token, returnPath=False, **kwargs):
        assert token == "secret-token"
        filename = os.path.basename(assetUrl)
        target = os.path.join(output_dir, filename)
        shutil.copyfile(filename, target)
        return target

    monkeypatch.setattr(session, "get", _fake_get)
    monkeypatch.setattr(morpc.req, "get_file_safely", _fake_get_file_safely)
    monkeypatch.setattr("morpc.frictionless.release.get_private_release_asset", _fake_private_asset)
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token")

    results = load_package(packageUrl, archiveDir=str(tmp_path / "cache"))

    assert set(results) == {"addresspoints-points", "addresspoints-ranges"}
    assert sorted(results["addresspoints-points"][0]["housenum"].tolist()) == ["100", "102"]


def test_load_package_old_bare_string_shape_raises_clear_error(tmp_path, monkeypatch):
    # A package.yaml written before #180/#181 (bare filename strings, not inline resource objects)
    # cannot be loaded through frictionless.Package() at all -- assert this fails with a clear,
    # actionable message rather than an AttributeError from treating a string like a dict.
    import os
    import shutil

    import frictionless as fl
    import requests
    import yaml

    (tmp_path / "old.package.yaml").write_text(yaml.dump({
        "name": "addresspoints",
        "version": "1.0.0",
        "resources": ["addresspoints-points.resource.yaml"],
    }))

    url = "https://github.com/morpc/morpc-parcels-standardize/releases/download/v2026.7.22/old.package.yaml"

    def _fake_package_ctor(path):
        raise fl.FrictionlessException(fl.errors.SchemeError(note="not found")) from requests.HTTPError("404")

    def _fake_private_asset(assetUrl, output_dir, token, returnPath=False, **kwargs):
        target = os.path.join(output_dir, os.path.basename(assetUrl))
        shutil.copyfile(str(tmp_path / "old.package.yaml"), target)
        return target

    monkeypatch.setattr(fl, "Package", _fake_package_ctor)
    monkeypatch.setattr("morpc.frictionless.release.get_private_release_asset", _fake_private_asset)
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token")

    with pytest.raises(RuntimeError):
        load_package(url, archiveDir=str(tmp_path / "cache"))
