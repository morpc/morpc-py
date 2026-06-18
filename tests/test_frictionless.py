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
