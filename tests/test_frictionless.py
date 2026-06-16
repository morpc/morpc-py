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
