import pytest


def test_get_landlords_no_records(client):
    response = client.get('/api/v1/landlords')
    expected_result = {
        'success': True,
        'data': [],
        'number_of_records': 0,
        'pagination': {
            'total_pages': 0,
            'total_records': 0,
            'current_page': '/api/v1/landlords?page=1'
        }
    }
    
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.get_json() == expected_result


def test_get_landlords(client, sample_data):
    response = client.get('/api/v1/landlords')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert len(response_data['data']) == 3
    assert response_data['number_of_records'] == 3
    assert response_data['pagination'] == {
            'total_pages': 1,
            'total_records': 3,
            'current_page': '/api/v1/landlords?page=1'
        }


def test_get_one_landlord(client, sample_data):
    response = client.get('/api/v1/landlords/1')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert len(response_data['data']) == 11
    assert response_data['data']['identifier'] == 'landlord1'
    assert response_data['data']['email'] == 'landlord1@wp.pl'
    assert response_data['data']['first_name'] == 'Jan'
    assert response_data['data']['last_name'] == 'Kowalski'
    assert response_data['data']['phone'] == '601-500-400'
    assert response_data['data']['address'] == 'Adres 1, ulica1, 1/5'
    assert response_data['data']['description'] == 'Opis landlord 1'


def test_register_landlord(client):
    response = client.post('/api/v1/landlords/register', 
                            json = {
                                "address": "testaddress", 
                                "description": "testdescription", 
                                "email": "testmail@wp.pl", 
                                "first_name": "testfirst_name", 
                                "identifier": "testidentifier", 
                                "last_name": "testlast_name",
                                "phone": "testphone",
                                "password": "testpassword"                                
                            })
    response_data = response.get_json()

    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True 
    assert response_data['token']
 

@pytest.mark.parametrize(
    'data,missing_field',
    [
        (
            {"address": "testaddress", "email": "testmail@wp.pl", 
            "first_name": "testfirst_name", "last_name": "testlast_name",
            "phone": "testphone", "password": "testpassword"
            }, 
            'identifier'
        ),
        (  
            {"address": "testaddress", "identifier": "testidentifier",
            "first_name": "testfirst_name", "last_name": "testlast_name",
            "phone": "testphone", "password": "testpassword"
            }, 
            'email'
        ), 
        (
            {"address": "testaddress", "identifier": "testidentifier",
            "email": "testmail@wp.pl", "last_name": "testlast_name",
            "phone": "testphone", "password": "testpassword"
            }, 
            'first_name'
        ), 
        (
            {"address": "testaddress", "identifier": "testidentifier",
            "first_name": "testfirst_name", "email": "testmail@wp.pl",
            "phone": "testphone", "password": "testpassword"
            }, 
            'last_name'
        ), 
        (
            {"address": "testaddress", "identifier": "testidentifier",
            "first_name": "testfirst_name", "last_name": "testlast_name",
            "email": "testmail@wp.pl", "password": "testpassword"
            }, 
            'phone'
        ), 
        (
            {"email": "testmail@wp.pl", "identifier": "testidentifier",
            "first_name": "testfirst_name", "last_name": "testlast_name",
            "phone": "testphone", "password": "testpassword"
            }, 
            'address'
        ), 
        (
            {"address": "testaddress", "identifier": "testidentifier",
            "first_name": "testfirst_name", "last_name": "testlast_name",
            "phone": "testphone", "email": "testmail@wp.pl"
            }, 
            'password'
        ) 
    ]
)
def test_register_landlord_missing_data(client, data, missing_field):
    response = client.post('/api/v1/landlords/register', 
                            json=data)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_login_landlord(client, landlord):
    response = client.post('/api/v1/landlords/login', 
                            json={
                                'identifier': landlord['identifier'],
                                'password': landlord['password']
                            })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert 'token' in response_data


def test_register_landlord_already_used_email(client, landlord):
    response = client.post('/api/v1/landlords/register', 
                            json = {
                                "address": landlord['address'], 
                                "description": landlord['description'], 
                                "email": landlord['email'], 
                                "first_name": landlord['first_name'], 
                                "identifier": landlord['identifier'], 
                                "last_name": landlord['last_name'],
                                "phone": landlord['phone'],
                                "password": landlord['password']                                
                            })
    response_data = response.get_json()
    print('response data message:', response_data['message'] )

    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False 
    assert 'token' not in response_data
    assert f'Landlord with identifier {landlord["identifier"]} already exists' \
        in response_data['message']  


    response = client.post('/api/v1/landlords/register', 
                            json = {
                                "address": landlord['address'], 
                                "description": landlord['description'], 
                                "email": landlord['email'], 
                                "first_name": landlord['first_name'], 
                                "identifier": 'newtestidentifier', 
                                "last_name": landlord['last_name'],
                                "phone": landlord['phone'],
                                "password": landlord['password']                                
                            })
    response_data = response.get_json()
    print('response data message:', response_data['message'] )

    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False 
    assert 'token' not in response_data
    assert f'Landlord with email {landlord["email"]} already exists' \
        in response_data['message'] 


def test_get_current_landlord(client, landlord, landlord_token):
    response = client.get('/api/v1/landlords/me', 
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == landlord['identifier']
    assert response_data['data']['first_name'] == landlord['first_name']
    assert response_data['data']['last_name'] == landlord['last_name']
    assert response_data['data']['address'] == landlord['address']
    assert response_data['data']['email'] == landlord['email']
    assert response_data['data']['description'] == landlord['description']
    assert response_data['data']['phone'] == landlord['phone']
    assert 'id' in response_data['data']
    assert 'created' in response_data['data']
    assert 'updated' in response_data['data']


def test_update_landlord_password(client, landlord, landlord_token):
    response = client.put('/api/v1/landlords/password',
                            json={
                                'current_password': landlord['password'],
                                'new_password': 'newlandlordpassword'
                            },
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == landlord['identifier']
    assert response_data['data']['first_name'] == landlord['first_name']
    assert response_data['data']['last_name'] == landlord['last_name']
    assert response_data['data']['address'] == landlord['address']
    assert response_data['data']['email'] == landlord['email']
    assert response_data['data']['description'] == landlord['description']
    assert response_data['data']['phone'] == landlord['phone']
    assert 'id' in response_data['data']
    assert 'created' in response_data['data']
    assert 'updated' in response_data['data']


def test_update_landlord_password_missing_token(client, landlord):
    response = client.put('/api/v1/landlords/password',
                            json={
                                'current_password': landlord['password'],
                                'new_password': 'newlandlordpassword'
                            })
    response_data = response.get_json()

    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    alert = 'Missing landlord token. Please login or register as landlord.'
    assert alert in response_data['message']


def test_update_landlord_password_invalid_password(client, landlord, landlord_token):
    response = client.put('/api/v1/landlords/password',
                            json={
                                'current_password': 'wrongpassword',
                                'new_password': 'newlandlordpassword'
                            },
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'Invalid password' in response_data['message']


def test_get_landlords_with_params(client, sample_data):
    response = client.get('/api/v1/landlords?fields=id,identifier,first_name&sort=-id&id[lte]=2')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data'] == [
                                        {
                                        "first_name": "Andrzej", 
                                        "id": 2, 
                                        "identifier": "landlord2"
                                        }, 
                                        {
                                        "first_name": "Jan", 
                                        "id": 1, 
                                        "identifier": "landlord1"
                                        }
                                    ]


def test_update_landlord_data(client, landlord_token):
    updated_landlord = {
        "identifier": "updatedidentifier",
        "email": "updatedemail@wp.pl",
        "address": "updated address",
        "first_name": "updated first name",
        "last_name": "updated last name",
        "phone": "updated phone",
        "description": "updated description"
    }
    response = client.put('/api/v1/landlords/data',
                            json=updated_landlord,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == updated_landlord['identifier']
    assert response_data['data']['email'] == updated_landlord['email']
    assert response_data['data']['address'] == updated_landlord['address']
    assert response_data['data']['first_name'] == updated_landlord['first_name']
    assert response_data['data']['last_name'] == updated_landlord['last_name']
    assert response_data['data']['phone'] == updated_landlord['phone']
    assert response_data['data']['description'] == updated_landlord['description']
