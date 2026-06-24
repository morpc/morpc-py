import sqlite3

import pandas as pd
import pytest

from morpc.frictionless import load_data


SCHEMA_YAML = """\
fields:
  - name: id
    type: integer
  - name: name
    type: string
"""


def _build_sqlite(dirpath, table="people", include_control=True):
    """Create a SQLite database plus resource/schema sidecars in dirpath. Returns the resource path."""
    dataPath = dirpath / "data.sqlite"
    con = sqlite3.connect(dataPath)
    df = pd.DataFrame({"id": [1, 2], "name": ["alice", "bob"]})
    df.to_sql(table, con, index=False)
    con.close()

    (dirpath / "data.schema.yaml").write_text(SCHEMA_YAML)

    resourceLines = [
        "name: people",
        "type: table",
        "path: data.sqlite",
        "format: sqlite",
        "schema: data.schema.yaml",
    ]
    if include_control:
        resourceLines += ["dialect:", "  sql:", f"    table: {table}"]
    resourcePath = dirpath / "data.resource.yaml"
    resourcePath.write_text("\n".join(resourceLines) + "\n")
    return resourcePath


def test_load_sqlite_with_table_name(tmp_path):
    resourcePath = _build_sqlite(tmp_path, table="people", include_control=False)
    data, resource, schema = load_data(str(resourcePath), tableName="people")
    assert list(data.columns) == ["id", "name"]
    assert data["id"].tolist() == [1, 2]
    assert data["name"].tolist() == ["alice", "bob"]
    assert pd.api.types.is_integer_dtype(data["id"])


def test_load_sqlite_table_name_from_control(tmp_path):
    resourcePath = _build_sqlite(tmp_path, table="people", include_control=True)
    data, resource, schema = load_data(str(resourcePath))
    assert data["name"].tolist() == ["alice", "bob"]


def test_load_sqlite_missing_table_name_raises(tmp_path):
    resourcePath = _build_sqlite(tmp_path, table="people", include_control=False)
    with pytest.raises(RuntimeError):
        load_data(str(resourcePath))


CAMEL_SCHEMA_YAML = """\
fields:
  - name: personId
    type: integer
  - name: fullName
    type: string
"""


def _build_sqlite_camel(dirpath, table="people"):
    """SQLite with lowercase columns plus an extra column, paired with a camelCase schema."""
    dataPath = dirpath / "data.sqlite"
    con = sqlite3.connect(dataPath)
    df = pd.DataFrame({
        "personid": [1, 2],
        "fullname": ["alice", "bob"],
        "extra": ["x", "y"],
    })
    df.to_sql(table, con, index=False)
    con.close()

    (dirpath / "data.schema.yaml").write_text(CAMEL_SCHEMA_YAML)
    resourcePath = dirpath / "data.resource.yaml"
    resourcePath.write_text("\n".join([
        "name: people",
        "type: table",
        "path: data.sqlite",
        "format: sqlite",
        "schema: data.schema.yaml",
    ]) + "\n")
    return resourcePath


def test_load_sqlite_restores_schema_case_and_selects_schema_fields(tmp_path):
    resourcePath = _build_sqlite_camel(tmp_path, table="people")
    data, resource, schema = load_data(str(resourcePath), tableName="people")
    # Only the schema fields are returned, with the schema's camelCase restored.
    assert list(data.columns) == ["personId", "fullName"]
    assert "extra" not in data.columns
    assert data["personId"].tolist() == [1, 2]
    assert data["fullName"].tolist() == ["alice", "bob"]
    assert pd.api.types.is_integer_dtype(data["personId"])


def test_load_sqlite_no_schema_returns_all_columns(tmp_path):
    resourcePath = _build_sqlite_camel(tmp_path, table="people")
    data, resource, schema = load_data(str(resourcePath), tableName="people", useSchema=None)
    # With no schema, all columns are returned as-is.
    assert list(data.columns) == ["personid", "fullname", "extra"]


def test_load_sqlite_schema_field_missing_from_table_raises(tmp_path):
    resourcePath = _build_sqlite_camel(tmp_path, table="people")
    # Schema references a field that does not exist in the SQLite table.
    (tmp_path / "data.schema.yaml").write_text(CAMEL_SCHEMA_YAML + "  - name: missingField\n    type: string\n")
    with pytest.raises(RuntimeError):
        load_data(str(resourcePath), tableName="people")


# --- load_data: spatial SQLite support ---

SPATIAL_SCHEMA_YAML = """\
fields:
  - name: id
    type: integer
"""


def _build_spatial_sqlite_resource(dirpath, table="parcels", geom_column="geom", include_control=True):
    """Create a spatial SQLite database (WKB BLOB geometry) plus resource/schema sidecars. Returns the resource path."""
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

    (dirpath / "data.schema.yaml").write_text(SPATIAL_SCHEMA_YAML)

    resourceLines = [
        "name: parcels",
        "type: table",
        "path: data.sqlite",
        "format: sqlite",
        "schema: data.schema.yaml",
    ]
    if include_control:
        resourceLines += ["dialect:", "  sql:", f"    table: {table}"]
    resourcePath = dirpath / "data.resource.yaml"
    resourcePath.write_text("\n".join(resourceLines) + "\n")
    return resourcePath


def test_load_data_spatial_sqlite_detects_geometry(tmp_path):
    import geopandas as gpd

    resourcePath = _build_spatial_sqlite_resource(tmp_path, table="parcels")
    data, resource, schema = load_data(str(resourcePath))
    assert isinstance(data, gpd.GeoDataFrame)
    assert data["id"].tolist() == [1, 2]
    assert list(data.geometry.geom_type) == ["Point", "Point"]
    assert pd.api.types.is_integer_dtype(data["id"])
    # WKB geometry carries no CRS, so epsg:4326 is assumed on read.
    assert data.crs == "epsg:4326"


def test_load_data_spatial_sqlite_custom_geometry_column(tmp_path):
    import geopandas as gpd

    resourcePath = _build_spatial_sqlite_resource(tmp_path, table="parcels", geom_column="shape")
    data, resource, schema = load_data(str(resourcePath), tableName="parcels")
    assert isinstance(data, gpd.GeoDataFrame)
    assert list(data.geometry.geom_type) == ["Point", "Point"]


def test_load_data_spatial_sqlite_target_crs(tmp_path):
    resourcePath = _build_spatial_sqlite_resource(tmp_path, table="parcels")
    data, resource, schema = load_data(str(resourcePath), targetCRS="epsg:3735")
    assert data.crs == "epsg:3735"


def test_load_data_nonspatial_sqlite_returns_plain_dataframe(tmp_path):
    import geopandas as gpd

    # A SQLite file with no WKB geometry column must still load as an ordinary DataFrame.
    resourcePath = _build_sqlite(tmp_path, table="people", include_control=True)
    data, resource, schema = load_data(str(resourcePath))
    assert not isinstance(data, gpd.GeoDataFrame)
    assert data["name"].tolist() == ["alice", "bob"]
