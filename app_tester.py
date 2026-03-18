#from fastapi.testclient import TestClient
#from dbm import sqlite3
#from urllib import response
#client = TestClient(app)
import pytest
import sqlite3
from src.app import app
# conftest.py
from src import database_commands as db
from flask import jsonify
#from flask.testing import FlaskClient
#client = app.test_client()  # in conftest.py

#### run with pytest tests/app_tester.py #####
######## endpoints ###############
    
def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json() == {"msg": "Hello Team"}


def test_create_item(client):
    response = client.post(
        "/",
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200

########### get endpoints ###########
def test_get_all_data(client, in_memory_db):
    # Use the yielded connection to pre-populate directly
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()

    response = client.get("/data/items")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    ]
    
    
def test_get_column(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()
    
    response = client.get("/data/items/column/title")
    assert response.status_code == 200
    assert response.get_json() == ["Foo Bar"]

def test_get_column_not_found(client):
    response = client.get("/data/items/column/nonexistent")
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Column not found"}

def test_get_id(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()
    
    response = client.get("/data/items/id/foobar")
    assert response.status_code == 200
    assert response.get_json() == {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}

def test_get_id_not_found(client):
    response = client.get("/data/items/id/doesnotexist")
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}

################ tests for put/update endpoints ###########################

def test_update(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()
    
    response = client.put("/data/items/id/foobar", json={"title": "Updated foo bar"})
    assert response.status_code == 200
    assert response.get_json() == "Item updated successfully"
    
    response = client.get("/data/items/id/foobar")
    assert response.get_json()["title"] == "Updated foo bar"

def test_update_not_found(client):
    response = client.put("/data/items/id/doesnotexist", json={"title": "Updated foo bar"})
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}
    
####################### insert #########################
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
def setup_reserved_db():
    """Helper: in-memory DB with the Transit_Table schema."""
    con = sqlite3.connect(":memory:")
    return con  # reserve_data calls create_transit_table itself


def test_reserve_data():
    con = setup_reserved_db()
    db.reserve_data(con, "Product_ID", 1, 10, "A", "B")

    result = db.get_all_data(con)

    # get_all_data returns {"Status": ["Reserved"], ...}
    assert "Status" in result
    assert "Reserved" in result["Status"]


def test_update_transit():
    con = setup_reserved_db()
    db.reserve_data(con, "Product_ID", 1, 10, "A", "B")
    db.update_transit(con, 2, "Product_ID", 1)  # status 2 = In_Transit

    result = db.get_all_data(con)
    assert "In_Transit" in result["Status"]


def test_reserve_invalid_type():
    con = setup_reserved_db()
    with pytest.raises(SystemExit):
        db.reserve_data(con, "Product_ID", [1, 2, 3], 10, "A", "B")
        
######## tests for delete endpoints ###########################   
def test_delete_all(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()
    
    response = client.delete("/")
    assert response.status_code == 200
    assert response.get_json()  == "Item deleted successfully"

def test_delete_by_column(client, in_memory_db):
    in_memory_db.execute(
        "INSERT INTO items VALUES (?, ?, ?)",
        ("foobar", "Foo Bar", "The Foo Barters")
    )
    in_memory_db.commit()
    
    response = client.delete("/data/items/column/id/foobar")
    assert response.status_code == 200
    assert response.get_json() == "Items with id = foobar deleted successfully"
    

def test_delete_by_column_not_found(client):
    response = client.delete("/data/items/column/id/doesnotexist")
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}
    