import sqlite3
import pytest
from src import database_commands as db


@pytest.fixture
def in_memory_conn():
    """Provides a fresh in-memory sqlite connection with a single table schema."""
    con = sqlite3.connect(":memory:")
    db.execute_single_query(con, """
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT
        )
    """)

    yield con

    db.close_connection(con)


def test_all_columns_and_get_tables_and_columns(in_memory_conn):
    schema = db.all_columns(in_memory_conn)

    assert "items" in schema
    assert schema["items"] == ["id", "title", "description"]

    tables, columns = db.get_tables_and_columns(schema)
    assert "items" in tables
    assert columns["items"] == schema["items"]


def test_get_insert_and_execute_single_query_and_get_functions(in_memory_conn):
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}

    insert_queries = db.get_insert(in_memory_conn, data)
    assert len(insert_queries) == 1

    sql, params = insert_queries[0]
    assert "INSERT INTO items" in sql
    assert params == ["foobar", "Foo Bar", "The Foo Barters"]

    db.execute_single_query(in_memory_conn, (sql, params))
    db.commit(in_memory_conn)

    assert db.get_table(in_memory_conn, "items") == ["foobar"]
    assert db.get_column(in_memory_conn, "items", "title") == ["Foo Bar"]

    rows = db.get_id(in_memory_conn, "items", "id", "foobar")
    assert rows and rows[0][0] == "foobar"
    assert rows[0][1] == "Foo Bar"

    all_data = db.get_all_data(in_memory_conn)
    assert all_data["id"] == ["foobar"]
    assert all_data["title"] == ["Foo Bar"]


def test_execute_multi_query_and_update(in_memory_conn):
    rows = [
        {"id": "a", "title": "A", "description": "a"},
        {"id": "b", "title": "B", "description": "b"},
    ]

    insert_sql = [db.get_insert(in_memory_conn, row)[0] for row in rows]
    db.execute_multi_query(in_memory_conn, insert_sql)
    db.commit(in_memory_conn)

    ids = set(db.get_table(in_memory_conn, "items"))
    assert ids == {"a", "b"}

    db.update(in_memory_conn, "items", "title", "BOO", "id", "a")
    titles = db.get_column(in_memory_conn, "items", "title")
    assert "BOO" in titles
    assert "B" in titles


def test_reserve_data_creates_transit_table_and_inserts_row(in_memory_conn):
    db.reserve_data(in_memory_conn, "id", "item1", 5, "Warehouse A", "Store B")
    db.commit(in_memory_conn)

    # Verify Transit_Table was created and contains the reserved row
    assert db.get_table(in_memory_conn, "Transit_Table") == ["item1"]
    assert db.get_column(in_memory_conn, "Transit_Table", "Status") == ["Reserved"]

    db.update_transit(in_memory_conn,2,"id","item1")
    assert db.get_column(in_memory_conn, "Transit_Table", "Status") == ["In_Transit"]
    var = db.get_column(in_memory_conn, "Transit_Table", "Status")[0]
    for s in db.Status:
            if s.value == var:
                assert var == db.Status.In_Transit.value
  

    rows = db.get_id(in_memory_conn, "Transit_Table", "id", "item1")
    assert rows and rows[0][2] == 5
    assert rows[0][3] == "Warehouse A"
    assert rows[0][4] == "Store B"

    # Verify the primary key column used the expected sql type for the value provided
    assert db.get_column_data_type(in_memory_conn, "Transit_Table", "id") == "TEXT"
