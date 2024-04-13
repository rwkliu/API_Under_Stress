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



def test_create_warrior(client):
    data = {
        "id": None,
        "name": "Vanilla Sky",
        "dob": "1985-02-14",
        "fight_skills": ["kungfu", "taekwondo"]
    }
    response = client.post('/warrior', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201

    response_data = response.json
    print("Response data post request:", response_data)

    assert 'id' in response_data
    data['id'] = response_data['id']
    assert data['id'] is not None

    assert 'message' in response_data
    assert response_data['message'] == 'Warrior created successfully'



def test_get_warrior(client):
    # Create a warrior and get its id
    data = {
        "id": None,
        "name": "Sunny Sky",
        "dob": "1985-02-14",
        "fight_skills": ["kungfu", "taekwondo"]
    }
    response = client.post('/warrior', data=json.dumps(data), content_type='application/json')
    response_data = response.json
    warrior_id = response_data['id'] # accessing id from dictionary

    # Retrieve the warrior by id
    getresponse = client.get(f'/warrior/{warrior_id}')
    print("getresponse.json get request:", getresponse.json) # it is returned as a list
    assert getresponse.status_code == 200

    warrior_data = getresponse.json
    assert warrior_data[0] == warrior_id


def test_search_warriors(client):
    search_name = "Vanilla Sky"
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
        "fight_skills": ["kungfu", "taekwondo"]
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
