import pytest
from api import app, connect_to_db
import json
import uuid
from validators import validate_fight_skills

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



def test_create_warrior(client):
    data = {
        "name": "Robin Ranjit",
        "dob": "1985-02-14",
        "fight_skills": ["KungFu", "Taekwondo"]
    }
    headers = {'Content-Type': 'application/json'}  # Specify content type in headers

    response = client.post('/warrior', json=data, headers=headers)
    assert response.status_code == 201

    # Extract ID from the location header
    location = response.headers.get('Location')
    assert location is not None
    warrior_id = location.split('/')[-1]

    # Check if warrior_id is a valid UUID
    assert len(warrior_id) == 36  # UUID length
    try:
        uuid.UUID(warrior_id)
    except ValueError:
        assert False, f"Invalid UUID: {warrior_id}"  # Fail the test if not a valid UUID


def test_get_warrior(client):
    # Create a warrior and get its uuid
    data = {
        "name": "Umesh Raj",
        "dob": "1985-02-14",
        "fight_skills": ["KungFu", "Taekwondo"]
    }
    response = client.post('/warrior', json=data)
    assert response.status_code == 201

    # Extract ID from the Location header
    location = response.headers.get('Location')
    assert location is not None
    warrior_id = location.split('/')[-1]   

    # Retrieve the warrior by id
    getresponse = client.get(f'/warrior/{warrior_id}')
    print("Debug-getresponse: ", getresponse)
    print("Debug-getresponse.json get request:", getresponse.json) # it is returned as a list
    assert getresponse.status_code == 200


def test_search_warriors(client):
    search_name = "Umesh Raj"
    response = client.get(f'/warrior?t={search_name}')
    assert response.status_code == 200

    warriors = response.json
    assert isinstance(warriors,list)
    assert len(warriors) > 0
    for warrior in warriors:
        assert search_name in warrior[1]


def test_count_warriors(client):
    response = client.get('/counting-warriors')
    assert response.status_code == 200

    response_data = response.json
    assert 'count' in response_data
    total_count = response_data['count']
    assert isinstance(total_count, int)
    assert total_count >= 0

def test_invalid_input_data(client):
    data = {
        "dob": "0000-00-00",
        "fight_skills": ["KungFu", "Taekwondo"]
    }
    response = client.post('/warrior', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400


def test_retrieve_non_existing_warrior(client):
    non_existing_id = 'nonExistingId'
    response = client.get(f'/warrior/{non_existing_id}')
    assert response.status_code == 404


def test_search_non_existing_warrior(client):
    search_name = "NonExistingName"
    response = client.get(f'/warrior?t={search_name}')
    assert response.status_code == 200
    assert len(response.json) == 0


def test_empty_request_parameter(client):
    response = client.get('/warrior')
    assert response.status_code == 400 

def test_invalid_fight_skills(client):
    data = {
        "name": "Test Warrior",
        "dob": "1990-01-01",
        "fight_skills": ["InvalidSkill", "AnotherInvalidSkill"]
    }
    response = client.post('/warrior', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    response_data = response.json
    assert 'message' in response_data
    assert response_data['message'] == 'Bad Request - Invalid fight skill'
