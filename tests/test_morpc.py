import os
import subprocess

import pytest

import morpc


class FakeCompleted:
    def __init__(self):
        self.stdout = ""
        self.stderr = ""


def test_curl_builds_expected_command(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['cmd'] = cmd
        calls['kwargs'] = kwargs
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    archive_dir = str(tmp_path / "input_data")
    morpc.curl("https://example.com/file.zip", archive_dir=archive_dir, verbose=False)

    expected_path = os.path.normpath(f'./{archive_dir}/file.zip')
    assert calls['cmd'] == ['curl', 'https://example.com/file.zip', '-o', expected_path]
    assert calls['kwargs']['shell'] is False
    assert calls['kwargs']['check'] is True


def test_curl_shell_passthrough(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['kwargs'] = kwargs
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    morpc.curl("https://example.com/file.zip", archive_dir=str(tmp_path / "d"), shell=True, verbose=False)
    assert calls['kwargs']['shell'] is True


def test_curl_uses_basename_when_no_filename(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['cmd'] = cmd
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    archive_dir = str(tmp_path / "d")
    morpc.curl("https://example.com/data/tiger.shp", archive_dir=archive_dir, verbose=False)
    assert calls['cmd'][-1] == os.path.normpath(f'./{archive_dir}/tiger.shp')


def test_curl_custom_filename(monkeypatch, tmp_path):
    calls = {}

    def fake_run(cmd, **kwargs):
        calls['cmd'] = cmd
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    archive_dir = str(tmp_path / "d")
    morpc.curl("https://example.com/file.zip", archive_dir=archive_dir, filename="renamed.zip", verbose=False)
    assert calls['cmd'][-1] == os.path.normpath(f'./{archive_dir}/renamed.zip')


def test_curl_creates_archive_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: FakeCompleted())

    archive_dir = tmp_path / "newdir"
    assert not archive_dir.exists()
    morpc.curl("https://example.com/file.zip", archive_dir=str(archive_dir), verbose=False)
    assert archive_dir.exists()


def test_curl_return_filepath(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: FakeCompleted())

    archive_dir = str(tmp_path / "d")
    result = morpc.curl(
        "https://example.com/file.zip",
        archive_dir=archive_dir,
        return_filepath=True,
        verbose=False,
    )
    assert result == os.path.normpath(f'./{archive_dir}/file.zip')


def test_curl_no_return_by_default(monkeypatch, tmp_path):
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: FakeCompleted())

    result = morpc.curl("https://example.com/file.zip", archive_dir=str(tmp_path / "d"), verbose=False)
    assert result is None


# --- load_spatial_data: SQLite support ---

def _build_spatial_sqlite(dirpath, table="parcels", geom_column="geom"):
    """Create a SQLite database with a WKB geometry column. Returns the file path."""
    import sqlite3
    from shapely.geometry import Point

    dataPath = dirpath / "data.sqlite"
    con = sqlite3.connect(dataPath)
    con.execute(f'CREATE TABLE "{table}" (id INTEGER, "{geom_column}" BLOB)')
    con.executemany(
        f'INSERT INTO "{table}" (id, "{geom_column}") VALUES (?, ?)',
        [(1, Point(0, 0).wkb), (2, Point(1, 1).wkb)],
    )
    con.commit()
    con.close()
    return dataPath


def test_load_spatial_data_sqlite(tmp_path):
    import geopandas as gpd

    dataPath = _build_spatial_sqlite(tmp_path, table="parcels")
    gdf = morpc.load_spatial_data(str(dataPath), layerName="parcels", verbose=False)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf["id"].tolist() == [1, 2]
    assert list(gdf.geometry.geom_type) == ["Point", "Point"]
    assert (gdf.geometry.x.tolist(), gdf.geometry.y.tolist()) == ([0.0, 1.0], [0.0, 1.0])
    # CRS defaults to epsg:4326
    assert gdf.crs == "epsg:4326"


def test_load_spatial_data_sqlite_requires_layer_name(tmp_path):
    dataPath = _build_spatial_sqlite(tmp_path, table="parcels")
    with pytest.raises(RuntimeError):
        morpc.load_spatial_data(str(dataPath), verbose=False)


def test_load_spatial_data_sqlite_custom_geometry_column(tmp_path):
    dataPath = _build_spatial_sqlite(tmp_path, table="parcels", geom_column="shape")
    gdf = morpc.load_spatial_data(str(dataPath), layerName="parcels", geometryColumn="shape", verbose=False)
    assert list(gdf.geometry.geom_type) == ["Point", "Point"]


def test_load_spatial_data_sqlite_custom_target_crs(tmp_path):
    dataPath = _build_spatial_sqlite(tmp_path, table="parcels")
    gdf = morpc.load_spatial_data(str(dataPath), layerName="parcels", targetCRS="epsg:3735", verbose=False)
    assert gdf.crs == "epsg:3735"
