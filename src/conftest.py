import pytest
# Each test posts data but the database persists between tests. 
# fixture to clear state:

@pytest.fixture(autouse=True)
def clear_db():
    client.delete("/")  # wipe before each test
    yield
