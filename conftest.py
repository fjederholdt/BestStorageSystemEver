import pytest
import sqlite3
from src.app import app
from src import database_commands as db


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch):
    """Fresh in-memory DB for every test. Patches app's db.connect()."""
    con = sqlite3.connect(":memory:")
    con.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            description TEXT
        )
    """)
    con.commit()

    monkeypatch.setattr("src.app.db.connect", lambda: con) 
    monkeypatch.setattr("src.app.db.close_connection", lambda c: None)

    yield con

    con.close()


@pytest.fixture
def client():
    """Flask test client with TESTING mode on."""
    app.config["TESTING"] = True
    return app.test_client()

    """
app.config["TESTING"]       # True = enables test mode, propagates exceptions
app.config["DEBUG"]         # True = enables debugger and auto-reloader
app.config["SECRET_KEY"]    # used for session signing and security
app.config["DATABASE"]      # not built-in, but a common custom key
    """