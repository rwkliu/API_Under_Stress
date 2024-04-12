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
    # print(response.status_code)
    # print(response.data)
    assert response.status_code == 200 
    assert response.data.decode('utf-8') == "Welcome to API Under Stress!" 
    


def test_create_warrior(client):
    data = {
        "id": None,
        "name": "Red Sky",
        "dob": "1985-02-14",
        "fight_skills": ["kungfu", "taekwondo"]
    }
    response = client.post('/warrior', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201

    response_data = response.json
    # print("Response data:", response_data)

    assert 'id' in response_data
    data['id'] = response_data['id']
    assert data['id'] is not None

    assert 'message' in response_data
    assert response_data['message'] == 'Warrior created successfully'

