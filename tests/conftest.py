import pytest
import sqlite3
from src import database_commands as db


@pytest.fixture(autouse=True)
def clear_db_before_each_test(monkeypatch):
    # Create a new in-memory database connection for each test
    con = sqlite3.connect(":memory:")
    
    # Create the items table in the in-memory database
    db.create_table(con, """
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # Patch the connect function to return the in-memory connection
    monkeypatch.setattr("src.app.db.connect", lambda: con)
    
    yield  # Test runs here
    
    db.close_connection(con)  # Destroy the in-memory database after the test