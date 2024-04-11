import pytest
from api import app, connect_to_db
import json 

@pytest.fixture
def client():
    app.config['TESTING'] = True #indicates the flask applicaiton running in test mode 
    with app.test_client() as client:
        yield client 

def test_default(client):
    response = client.get('/') 
    print(response.status_code)
    print(response.data)
    assert response.status_code == 200 
    assert response.data.decode('utf-8') == "Welcome to API Under Stress!"