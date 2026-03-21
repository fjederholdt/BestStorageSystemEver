import pytest # test framework
import sqlite3 # database interaction
from src.app import app # Flask application
from src import database_commands as db # database functions

@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch):
    """Fresh in-memory DB for every test. Patches app's db.connect()."""
    con = sqlite3.connect(":memory:") # In-memory DB (fast, temporary)
    con.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            description TEXT
        )
    """)
    con.commit()

    monkeypatch.setattr("src.app.db.connect", lambda: con) # Replaces real DB connection with test DB
    monkeypatch.setattr("src.app.db.close_connection", lambda c: None)

    yield con # Gives DB to test

    con.close()

# Creates Flask test client:
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

import os.path

# Log failed tests into a file
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.failed:
        mode = "a" if os.path.exists("failures") else "w"
        # Saves full error traceback
        with open("failures", mode) as f:
            f.write(rep.longreprtext + "\n")