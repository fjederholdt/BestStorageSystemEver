"""This test suite validates a Flask-based REST API that performs CRUD operations.
The tests are written using pytest and use an in-memory SQLite database to ensure isolation and 
repeatability.

The test setup consists of two main components:
- Test File (app_tester.py) Contains test cases that simulate HTTP requests and validate responses.
- Configuration File (conftest.py) Defines reusable fixtures:

- In-Memory Database Fixture - A fresh SQLite database is created for each test: 
    uses sqlite3.connect(":memory:")
    creates items table with schema:
        id (TEXT, primary key)
        title (TEXT, required)
        description (TEXT)

- Monkeypatching - Database connections inside the application are overridden:
    db.connect() returns in-memory DB
    db.close_connection() disabled

This ensures: no real database is used, each test runs in isolation

- Flask Test Client - A test client is created with:

    app.config["TESTING"] = True
    app.test_client()

This allows simulation of HTTP requests such as: GET, POST, PUT

How to Run the Tests
Run all tests with verbose output and HTML report:
pytest tests/app_tester.py -v --html=report.html --self-contained-html --tb=short
or 
pytest tests/app_tester.py -v

Run a single test by name:
pytest tests/app_tester.py::test_get_all_data -v

Print all registered Flask routes (useful for debugging):
pytest tests/app_tester.py::test_show_routes -s

Install the HTML report plugin if not already installed:
pip install pytest-html

    """

import pytest # test framework
import sqlite3 # database interaction
from src.app import app # Flask application
from src import database_commands as db # database functions
from flask import url_for # generates endpoint URLs dynamically

######## endpoints ###############
# Test the main GET endpoint
def test_read_main(client):
    with app.test_request_context(): # Creates a fake request context so url_for works
        url = url_for("get_item") # "get_item" = Flask route function name
    response = client.get(url) # Simulates HTTP GET request
    assert response.status_code == 200
    assert response.get_json() == {"msg": "Hello Team"}

# Test POST endpoint (create item)
def test_create_item(client):
    with app.test_request_context():
        url = url_for("post_item")
    # Sends JSON payload
    response = client.post(
        url,
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    # Verifies only status
    assert response.status_code == 200

########### get endpoints ###########

def test_get_all_data(client, in_memory_db):
    # Inserts test data into temporary DB
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    with app.test_request_context():
        url = url_for("get_all_data", table="items")
    response = client.get(url)
    assert response.status_code == 200
    # Ensures API returns correct structure
    assert response.get_json() == [
        {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    ]
# Tests retrieving a single column
def test_get_column(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    with app.test_request_context():
        url = url_for("get_column", table="items", column="title")
    response = client.get(url)
    assert response.status_code == 200
    assert response.get_json() == ["Foo Bar"]
    
# Tests error handling
def test_get_column_not_found(client):
    with app.test_request_context():
        url = url_for("get_column", table="items", column="nonexistent")
    response = client.get(url)
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Column not found"}

# Tests retrieving single row by ID
def test_get_id(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    with app.test_request_context():
        url = url_for("get_by_id", table="items", id="foobar")
    response = client.get(url)
    assert response.status_code == 200
    assert response.get_json() == {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
# Tests missing item
def test_get_id_not_found(client):
    with app.test_request_context():
        url = url_for("get_by_id", table="items", id="doesnotexist")
    response = client.get(url)
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}

################ put/update endpoints ###########################

def test_update(client, in_memory_db):
    in_memory_db.execute(
        # insert new item
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    with app.test_request_context():
        url = url_for("update_by_id", table="items", id="foobar")
    # updated 
    response = client.put(url, json={"title": "Updated foo bar"})
    assert response.status_code == 200
    # verification
    assert response.get_json() == "Item updated successfully"

    with app.test_request_context():
        url = url_for("get_by_id", table="items", id="foobar")
    # verify db change
    response = client.get(url)
    assert response.get_json()["title"] == "Updated foo bar"

# Tests updating non-existing item
def test_update_not_found(client):
    with app.test_request_context():
        url = url_for("update_by_id", table="items", id="doesnotexist")
    response = client.put(url, json={"title": "Updated foo bar"})
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}
    
####################### insert #########################
#Validate that the SQL insert query and corresponding values are generated correctly.
#ensures proper mapping between dictionary data and SQL columns and Correct ordering of values (critical for SQL execution)
def test_get_insert_cols():
    cols = ["id", "title", "description"]
    data = {
        "id": "1",
        "title": "updated Foo",
        "description": "updated foo barters"
    }
    sql, values = db.get_insert_cols("items", cols, data)
    assert "INSERT INTO items" in sql
    assert values == ["1", "updated Foo", "updated foo barters"]

####### reserve system ######
#Unlike previous tests, this function does not create tables explicitly, so the tested functions must handle schema creation internally.

def setup_reserved_db():
    #Creates a temporary database connection for reservation-related tests.
    con = sqlite3.connect(":memory:")
    return con
#Verify that a reservation is correctly created.
# The system tracks item states using a "Status" field "Reserved" indicates successful reservation
def test_reserve_data():
    con = setup_reserved_db()
    db.reserve_data(con, "Product_ID", 1, 10, "A", "B")
    result = db.get_all_data(con)
    assert "Status" in result
    assert "Reserved" in result["Status"]
#Verify that a reserved item can transition to "In Transit" state.
def test_update_transit():
    con = setup_reserved_db()
    db.reserve_data(con, "Product_ID", 1, 10, "A", "B")
    db.update_transit(con, 2, "Product_ID", 1)
    result = db.get_all_data(con)
    assert "In_Transit" in result["Status"]
#Ensure invalid input types are handled properly.
#Input validation is enforced. Lists are not allowed where scalar values are expected
def test_reserve_invalid_type():
    con = setup_reserved_db()
    with pytest.raises(SystemExit):
        db.reserve_data(con, "Product_ID", [1, 2, 3], 10, "A", "B")

######## delete endpoints ###########################
#Verify deletion of all records.
#Deletes all entries in the table
# Returns confirmation message
def test_delete_all(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    with app.test_request_context():
        url = url_for("delete_item")
    response = client.delete(url)
    assert response.status_code == 200
    assert response.get_json() == "Item deleted successfully"
#Delete specific records based on column value.
# Filters records using column-value pair
# Deletes matching rows only
def test_delete_by_column(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    with app.test_request_context():
        url = url_for("delete_by_column", table="items", column="id", value="foobar")
    response = client.delete(url)
    assert response.status_code == 200
    assert response.get_json() == "Items with id = foobar deleted successfully"
# Handle deletion of non-existing records.
def test_delete_by_column_not_found(client):
    with app.test_request_context():
        url = url_for("delete_by_column", table="items", column="id", value="doesnotexist")
    response = client.delete(url)
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}