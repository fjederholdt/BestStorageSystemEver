from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)

###########################

import pytest

@pytest.fixture(autouse=True)
def clear_db():
    client.delete("/")  # wipe before each test
    yield

###############################


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_create_item():
    response = client.post(
        "/",
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }
    
######## tests for delete endpoints ###########################   
def test_delete_all():
    response = client.delete("/")
    assert response.status_code == 200
    assert response.json() == "All items deleted successfully"

def test_delete_by_column():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.delete("/data/items/column/id/foobar")
    assert response.status_code == 200
    assert response.json() == "Item deleted successfully"

def test_delete_by_column_not_found():
    response = client.delete("/data/items/column/id/doesnotexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
    
############### tests for get endpoints ###########################

def test_get_all_data():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.get("/data/items")
    assert response.status_code == 200
    assert response.json() == [data]
    
def test_get_column():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    response = client.get("/data/items/column/title")
    assert response.status_code == 200
    assert response.json() == ["Foo Bar"]

def test_get_id():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data) 
    response = client.get("/data/items/id/foobar")
    assert response.status_code == 200
    assert response.json() == {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}

def test_get_id_not_found():
    response = client.get("/data/items/id/doesnotexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

################ tests for put/update endpoints ###########################

def test_update():
    data = {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    client.post("/", json=data)
    update_data = {"title": "Updated foo bar"}
    response = client.put("/data/items/id/foobar", json=update_data)
    assert response.status_code == 200
    assert response.json() == "Item updated successfully"
