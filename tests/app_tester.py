#from fastapi.testclient import TestClient
#from dbm import sqlite3
#from urllib import response
from src.app import app
#client = TestClient(app)
import pytest
import sqlite3

# conftest.py
import database_commands as db

from flask.testing import FlaskClient
client = app.test_client()


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json() == {"msg": "Hello World"}

def test_create_item():
    response = client.post(
        "/",
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }
    
######## tests for delete endpoints ###########################   
def test_delete_all():
    response = client.delete("/")
    assert response.status_code == 200
    assert response.get_json() == "All items deleted successfully"

def test_delete_by_column():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.delete("/data/items/column/id/foobar")
    assert response.status_code == 200
    assert response.get_json() == "Items with id = foobar deleted successfully"
    

def test_delete_by_column_not_found():
    response = client.delete("/data/items/column/id/doesnotexist")
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}
    
############### tests for get endpoints ###########################

def test_get_all_data():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.get("/data/items")
    assert response.status_code == 200
    assert response.get_json() == [{"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}]

def test_get_all_data_empty():
    response = client.get("/data/items")
    assert response.status_code == 200
    assert response.get_json() == []
    
    
def test_get_column():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.get("/data/items/column/title")
    assert response.status_code == 200
    assert response.get_json() == ["Foo Bar"]

def test_get_column_not_found():
    response = client.get("/data/items/column/nonexistent")
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Column not found"}

def test_get_id():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data) 
    response = client.get("/data/items/id/foobar")
    assert response.status_code == 200
    assert response.get_json() == {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}

def test_get_id_not_found():
    response = client.get("/data/items/id/doesnotexist")
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}

################ tests for put/update endpoints ###########################

def test_update():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.put("/data/items/id/foobar", json={"title": "Updated foo bar"})
    assert response.status_code == 200
    assert response.get_json() == "Item updated successfully"
    
    response = client.get("/data/items/id/foobar")
    assert response.get_json()["title"] == "Updated foo bar"

def test_update_not_found():
    response = client.put("/data/items/id/doesnotexist", json={"title": "Updated foo bar"})
    assert response.status_code == 404
    assert response.get_json() == {"detail": "Item not found"}

