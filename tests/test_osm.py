import json

import geopandas as gpd
import osmnx as ox
import pytest
from osmnx._errors import InsufficientResponseError, ResponseStatusCodeError
from shapely.geometry import Point, box, mapping, shape

from morpc.osm import (
    OsmControl,
    OsmQueryPackage,
    OsmResource,
    OsmSchema,
    fetch_changesets,
    fetch_osm_features,
    summarize_changesets,
)
from morpc.osm.osm import (
    _changesets_to_gdf,
    _describe_scope,
    _quarter_polygon,
    _reconstruct_scope,
    _resolve_scope,
    _which_scope,
)

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


# --- changeset monitoring ---

CHANGESET_BOX = box(-83.05, 39.95, -83.04, 39.96)


def _changeset_feature(cid, date, uid=1, create=5, modify=2, delete=0, is_suspect=False, checked=False, harmful=None):
    return {
        "id": cid,
        "type": "Feature",
        "geometry": mapping(CHANGESET_BOX),
        "properties": {
            "user": f"user{uid}",
            "uid": uid,
            "date": date,
            "editor": "iD 2.0",
            "comment": "add buildings",
            "source": "",
            "create": create,
            "modify": modify,
            "delete": delete,
            "comments_count": 0,
            "is_suspect": is_suspect,
            "harmful": harmful,
            "checked": checked,
            "check_user": "reviewer" if checked else None,
            "check_date": "2026-08-10T00:00:00Z" if checked else None,
            "reasons": [{"name": "possible import"}] if is_suspect else [],
        },
    }


class _FakeResponse:
    def __init__(self, payload, status_code=200, headers=None):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(f"unexpected status {self.status_code}")


def _fake_osmcha(pages, captured=None, fail_first_with=None, raise_first=None):
    """Return a requests.get stand-in that serves `pages` (a list of feature lists)."""
    state = {"429s_left": 1 if fail_first_with else 0, "raises_left": 1 if raise_first else 0}

    def _get(url, params=None, headers=None, timeout=None):
        if captured is not None:
            captured.append(params)
        if state["raises_left"]:
            state["raises_left"] -= 1
            raise raise_first
        if state["429s_left"]:
            state["429s_left"] -= 1
            return _FakeResponse({}, status_code=429, headers={"Retry-After": "0"})
        page = params.get("page", 1)
        if page > len(pages):
            return _FakeResponse({"features": [], "next": None})
        has_next = page < len(pages)
        return _FakeResponse({"features": pages[page - 1], "next": "http://next" if has_next else None})

    return _get


def test_fetch_changesets_requires_token(monkeypatch):
    monkeypatch.delenv("OSMCHA_TOKEN", raising=False)
    with pytest.raises(ValueError):
        fetch_changesets(polygon=POLY, start="2026-08-01", end="2026-08-07")


def test_fetch_changesets_paginates_and_types_result(monkeypatch):
    pages = [
        [_changeset_feature(1, "2026-08-01T10:00:00Z", uid=1, is_suspect=True, checked=True)],
        [_changeset_feature(2, "2026-08-04T12:00:00Z", uid=2)],
    ]
    monkeypatch.setattr("morpc.osm.osm.requests.get", _fake_osmcha(pages))
    monkeypatch.setattr("morpc.osm.osm.time.sleep", lambda s: None)

    gdf = fetch_changesets(polygon=POLY, start="2026-08-01", end="2026-08-07", token="x")

    assert list(gdf["id"]) == [1, 2]
    assert gdf.crs == "EPSG:4326"
    assert str(gdf["date"].dt.tz) == "UTC"
    assert list(gdf["edits"]) == [7, 7]
    assert gdf.loc[0, "is_suspect"] and not gdf.loc[1, "is_suspect"]


def test_fetch_changesets_sends_scope_and_filter_params(monkeypatch):
    captured = []
    monkeypatch.setattr("morpc.osm.osm.requests.get", _fake_osmcha([[]], captured=captured))
    monkeypatch.setattr("morpc.osm.osm.time.sleep", lambda s: None)

    fetch_changesets(bbox=(-83.1, 39.9, -83.0, 40.0), start="2026-08-01", end="2026-08-07",
                     token="x", area_lt=1.5, only_suspect=True)

    params = captured[0]
    assert params["date__gte"] == "2026-08-01" and params["date__lte"] == "2026-08-07"
    assert params["area_lt"] == 1.5 and params["is_suspect"] == "True"
    assert shape(json.loads(params["geometry"])).equals(box(-83.1, 39.9, -83.0, 40.0))


def test_fetch_changesets_retries_on_429(monkeypatch):
    pages = [[_changeset_feature(1, "2026-08-01T10:00:00Z")]]
    monkeypatch.setattr("morpc.osm.osm.requests.get", _fake_osmcha(pages, fail_first_with=429))
    monkeypatch.setattr("morpc.osm.osm.time.sleep", lambda s: None)

    gdf = fetch_changesets(polygon=POLY, start="2026-08-01", token="x")
    assert list(gdf["id"]) == [1]


def test_fetch_changesets_retries_on_transient_network_error(monkeypatch):
    import requests

    pages = [[_changeset_feature(1, "2026-08-01T10:00:00Z")]]
    monkeypatch.setattr(
        "morpc.osm.osm.requests.get",
        _fake_osmcha(pages, raise_first=requests.exceptions.ReadTimeout("slow")),
    )
    monkeypatch.setattr("morpc.osm.osm.time.sleep", lambda s: None)

    gdf = fetch_changesets(polygon=POLY, start="2026-08-01", token="x")
    assert list(gdf["id"]) == [1]


def test_changesets_to_gdf_empty_is_empty_frame():
    gdf = _changesets_to_gdf([])
    assert gdf.empty


def test_summarize_changesets_rolls_up_by_period():
    features = [
        _changeset_feature(1, "2026-08-03T10:00:00Z", uid=1, is_suspect=True, checked=True),
        _changeset_feature(2, "2026-08-04T10:00:00Z", uid=1),
        _changeset_feature(3, "2026-08-11T10:00:00Z", uid=2, harmful=True, checked=True),
    ]
    summary = summarize_changesets(_changesets_to_gdf(features), freq="W")

    assert list(summary["changeset_count"]) == [2, 1]
    assert list(summary["distinct_users"]) == [1, 1]
    assert list(summary["suspect_count"]) == [1, 0]
    assert list(summary["harmful_count"]) == [0, 1]
    assert list(summary["reviewed_count"]) == [1, 1]


def test_summarize_changesets_empty_input():
    assert summarize_changesets(_changesets_to_gdf([])).empty
