import geopandas as gpd
import osmnx as ox
import pytest
from osmnx._errors import InsufficientResponseError, ResponseStatusCodeError
from shapely.geometry import Point, box, mapping, shape

from morpc.osm import OsmControl, OsmQueryPackage, OsmResource, OsmSchema, fetch_osm_features
from morpc.osm.osm import _describe_scope, _quarter_polygon, _reconstruct_scope, _resolve_scope, _which_scope

POLY = box(-83.1, 39.9, -83.0, 40.0)


@pytest.fixture(autouse=True)
def _chdir_tmp_path(tmp_path, monkeypatch):
    # Matches the convention in tests/test_gpkg.py: archived resources use relative paths from cwd.
    monkeypatch.chdir(tmp_path)


def _gdf(n=1):
    return gpd.GeoDataFrame(
        {"building": ["yes"] * n, "name": [f"f{i}" for i in range(n)]},
        geometry=[Point(i, i) for i in range(n)],
        crs="epsg:4326",
    )


# --- scope helpers ---

def test_which_scope_requires_exactly_one():
    assert _which_scope(POLY, None, None) == "polygon"
    with pytest.raises(ValueError):
        _which_scope(None, None, None)
    with pytest.raises(ValueError):
        _which_scope(POLY, "place", None)


def test_resolve_scope_polygon_passthrough():
    assert _resolve_scope(polygon=POLY) is POLY


def test_resolve_scope_bbox_builds_box():
    resolved = _resolve_scope(bbox=(-83.1, 39.9, -83.0, 40.0))
    assert resolved.equals(POLY)


def test_resolve_scope_place_geocodes(monkeypatch):
    boundary = gpd.GeoDataFrame(geometry=[POLY], crs="epsg:4326")
    monkeypatch.setattr(ox, "geocode_to_gdf", lambda place: boundary)
    resolved = _resolve_scope(place="Franklin County, Ohio")
    assert resolved.equals(POLY)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"polygon": POLY},
        {"bbox": (-83.1, 39.9, -83.0, 40.0)},
        {"place": "Franklin County, Ohio"},
    ],
)
def test_describe_and_reconstruct_scope_round_trip(kwargs):
    scope_type, scope = _describe_scope(**kwargs)
    polygon, place, bbox = _reconstruct_scope(scope_type, scope)
    resolved = _resolve_scope(polygon=polygon, place=place, bbox=bbox) if place is None else None
    if "polygon" in kwargs:
        assert resolved.equals(kwargs["polygon"])
    elif "bbox" in kwargs:
        assert resolved.equals(box(*kwargs["bbox"]))
    else:
        assert place == kwargs["place"]


def test_quarter_polygon_splits_into_four():
    parts = _quarter_polygon(POLY)
    assert len(parts) == 4
    for part in parts:
        assert POLY.contains(part) or POLY.equals(part.union(POLY))


# --- fetch_osm_features: success, split, fallback, exhaustion ---

def test_fetch_succeeds_on_first_try(monkeypatch):
    calls = []

    def fake(polygon, tags):
        calls.append(polygon)
        return _gdf(2)

    monkeypatch.setattr(ox, "features_from_polygon", fake)
    result = fetch_osm_features({"building": True}, polygon=POLY, overpass_endpoints=["http://mirrorA"])
    assert len(result) == 2
    assert len(calls) == 1


def test_fetch_returns_empty_frame_on_insufficient_response(monkeypatch):
    calls = []

    def fake(polygon, tags):
        calls.append(polygon)
        raise InsufficientResponseError("nothing here")

    monkeypatch.setattr(ox, "features_from_polygon", fake)
    result = fetch_osm_features({"building": True}, polygon=POLY, overpass_endpoints=["http://mirrorA"])
    assert len(result) == 0
    # A legitimate "nothing here" answer must not trigger a split into more requests.
    assert len(calls) == 1


def test_fetch_splits_on_failure_then_succeeds(monkeypatch):
    calls = []

    def fake(polygon, tags):
        calls.append(polygon)
        if len(calls) == 1:
            raise ResponseStatusCodeError("too big")
        return _gdf(1)

    monkeypatch.setattr(ox, "features_from_polygon", fake)
    result = fetch_osm_features({"building": True}, polygon=POLY, overpass_endpoints=["http://mirrorA"], max_split_depth=4)
    assert len(calls) == 5  # 1 failed whole-area request + 4 successful quadrant requests
    assert len(result) == 4


def test_fetch_falls_back_to_next_mirror_after_split_exhausted(monkeypatch):
    mirrors_seen = []

    def fake(polygon, tags):
        mirrors_seen.append(ox.settings.overpass_url)
        if ox.settings.overpass_url == "http://mirrorA":
            raise ResponseStatusCodeError("down")
        return _gdf(1)

    monkeypatch.setattr(ox, "features_from_polygon", fake)
    result = fetch_osm_features(
        {"building": True}, polygon=POLY,
        overpass_endpoints=["http://mirrorA", "http://mirrorB"], max_split_depth=0,
    )
    assert len(result) == 1
    assert "http://mirrorA" in mirrors_seen
    assert "http://mirrorB" in mirrors_seen


def test_fetch_raises_after_every_mirror_exhausted(monkeypatch):
    def fake(polygon, tags):
        raise ResponseStatusCodeError("always down")

    monkeypatch.setattr(ox, "features_from_polygon", fake)
    with pytest.raises(ResponseStatusCodeError):
        fetch_osm_features(
            {"building": True}, polygon=POLY,
            overpass_endpoints=["http://mirrorA", "http://mirrorB"], max_split_depth=0,
        )


def test_fetch_requires_exactly_one_scope():
    with pytest.raises(ValueError):
        fetch_osm_features({"building": True})


def test_fetch_requires_name_to_archive(monkeypatch, tmp_path):
    monkeypatch.setattr(ox, "features_from_polygon", lambda polygon, tags: _gdf(1))
    with pytest.raises(ValueError):
        fetch_osm_features({"building": True}, polygon=POLY, archive_dir=str(tmp_path))


# --- OsmSchema ---

def test_schema_infers_string_fields_from_columns():
    schema = OsmSchema.from_geodataframe(_gdf(2))
    assert [f.name for f in schema.fields] == ["building", "name"]
    assert all(f.type == "string" for f in schema.fields)


# --- OsmResource ---

def test_from_query_builds_descriptor_without_fetching(monkeypatch):
    monkeypatch.setattr(ox, "features_from_polygon", lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not fetch")))
    resource = OsmResource.from_query("Franklin County", {"building": True}, polygon=POLY)
    assert resource.name == "franklin-county"
    assert resource.type == "osm"
    control = OsmControl.from_dialect(resource.dialect)
    assert control.tags == {"building": True}
    assert control.scope_type == "polygon"
    assert shape(control.scope).equals(POLY)


def test_to_geodataframe_replays_query_and_attaches_schema(monkeypatch):
    monkeypatch.setattr(ox, "features_from_polygon", lambda polygon, tags: _gdf(2))
    resource = OsmResource.from_query("Franklin County", {"building": True}, polygon=POLY, overpass_endpoints=["http://mirrorA"])
    gdf = resource.to_geodataframe()
    assert len(gdf) == 2
    assert [f.name for f in resource.schema.fields] == ["building", "name"]


# --- archiving ---

def test_archive_writes_dense_package_with_unique_resource_names(monkeypatch, tmp_path):
    monkeypatch.setattr(ox, "features_from_polygon", lambda polygon, tags: _gdf(2))

    fetch_osm_features(
        {"building": True}, polygon=POLY, name="franklin",
        overpass_endpoints=["http://mirrorA"], archive_dir=str(tmp_path), version="2026.1.1",
    )

    assert (tmp_path / "franklin.gpkg").exists()
    assert (tmp_path / "franklin.schema.yaml").exists()
    assert (tmp_path / "franklin.package.yaml").exists()

    import frictionless
    package = frictionless.Package(str(tmp_path / "franklin.package.yaml"))
    names = [r.name for r in package.resources]
    assert len(names) == len(set(names))

    types = {r.type for r in package.resources}
    assert types == {"osm", "gpkg"}

    gpkgResource = next(r for r in package.resources if r.type == "gpkg")
    readback = gpkgResource.to_geodataframe()
    assert len(readback) == 2

    osmResource = next(r for r in package.resources if r.type == "osm")
    control = OsmControl.from_dialect(osmResource.dialect)
    assert control.tags == {"building": True}


# --- OsmQueryPackage ---

def test_from_query_never_fetches(monkeypatch):
    monkeypatch.setattr(
        ox, "features_from_polygon",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not fetch")),
    )
    package = OsmQueryPackage.from_query("Franklin County", {"building": True}, polygon=POLY, version="2026.1.1")
    assert isinstance(package, __import__("frictionless").Package)
    assert package.type == "osm-query"
    assert len(package.resources) == 1
    assert package.resources[0].type == "osm"


def test_save_writes_a_single_file_with_no_data(monkeypatch, tmp_path):
    monkeypatch.setattr(
        ox, "features_from_polygon",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not fetch")),
    )
    package = OsmQueryPackage.from_query("franklin", {"building": True}, polygon=POLY, version="2026.1.1")
    path = package.save(str(tmp_path))

    assert path == str(tmp_path / "franklin.package.yaml")
    assert list(tmp_path.iterdir()) == [tmp_path / "franklin.package.yaml"]


def test_saved_package_reloads_as_osmquerypackage_via_plain_frictionless(tmp_path):
    import frictionless

    package = OsmQueryPackage.from_query("franklin", {"building": True}, polygon=POLY, version="2026.1.1")
    path = package.save(str(tmp_path))

    # Round-tripping through the generic frictionless.Package() constructor -- not a morpc.osm-specific
    # loader -- must still come back as OsmQueryPackage, the same way GpkgResource/ArcGISResource
    # already round-trip through frictionless.Resource(). Requires morpc.osm to have been imported
    # (registers the plugin), same tradeoff those existing types already make.
    reloaded = frictionless.Package(path)
    assert isinstance(reloaded, OsmQueryPackage)
    assert isinstance(reloaded.resources[0], OsmResource)

    control = OsmControl.from_dialect(reloaded.resources[0].dialect)
    assert control.tags == {"building": True}
    assert shape(control.scope).equals(POLY)


def test_fetch_delegates_to_fetch_osm_features(monkeypatch):
    calls = []

    def fake(polygon, tags):
        calls.append(polygon)
        return _gdf(3)

    monkeypatch.setattr(ox, "features_from_polygon", fake)
    package = OsmQueryPackage.from_query(
        "franklin", {"building": True}, polygon=POLY, overpass_endpoints=["http://mirrorA"],
    )
    gdf = package.fetch()
    assert len(gdf) == 3
    assert len(calls) == 1


def test_fetch_can_archive(monkeypatch, tmp_path):
    monkeypatch.setattr(ox, "features_from_polygon", lambda polygon, tags: _gdf(2))
    package = OsmQueryPackage.from_query(
        "franklin", {"building": True}, polygon=POLY, overpass_endpoints=["http://mirrorA"],
    )

    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    package.fetch(archive_dir=str(archive_dir), version="2026.1.1")

    assert (archive_dir / "franklin.gpkg").exists()
    assert (archive_dir / "franklin.package.yaml").exists()

    # The snapshot file itself is untouched by fetch() -- it stays a static, data-free declaration.
    snapshot_dir = tmp_path / "snapshot"
    snapshot_dir.mkdir()
    snapshot_path = package.save(str(snapshot_dir))
    assert list(snapshot_dir.iterdir()) == [snapshot_dir / "franklin.package.yaml"]
