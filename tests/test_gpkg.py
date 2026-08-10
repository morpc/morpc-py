import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from morpc.frictionless import create_gpkgresource, create_package, load_data, load_resource, validate_resource
from morpc.frictionless.gpkg import GpkgControl, GpkgResource


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
