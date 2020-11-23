import pytest


def test_get_all_flats_no_records(client):
    response = client.get('/api/v1/flats')
    response_data = response.get_json()
    expected_result = {
        'success': True,
        'data': [],
        'number_of_records': 0,
        'pagination': {
            'total_pages': 0,
            'total_records': 0,
            'current_page': '/api/v1/flats?page=1'
        }
    }    
    
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data == expected_result


def test_get_all_flats(client, sample_data):
    response = client.get('/api/v1/flats')
    response_data = response.get_json()   
    
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert len(response_data['data']) == 5
    assert response_data['number_of_records'] == 5
    assert response_data['pagination'] == {
            'total_pages': 2,
            'total_records': 6,
            'current_page': '/api/v1/flats?page=1',
            'next_page': '/api/v1/flats?page=2'
        }


def test_get_all_flats_with_params(client, sample_data):
    response = client.get('/api/v1/flats?fields=id,identifier&sort=-id&id[gte]=2&limit=2&page=2')
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['number_of_records'] == 2
    # assert response_data['pagination'] == {
    #         "current_page": "/api/v1/flats?page=2&fields=id,identifier&sort=-id&id[gte]=2&limit=2", 
    #         "next_page": "/api/v1/flats?page=3&fields=id,identifier&sort=-id&id[gte]=2&limit=2", 
    #         "previous_page": "/api/v1/flats?page=1&fields=id,identifier&sort=-id&id[gte]=2&limit=2", 
    #         "total_pages": 3, 
    #         "total_records": 5
    #     }
    assert response_data['data'] == [
            {
            "id": 4, 
            "identifier": "Chopina 5"
            }, 
            {
            "id": 3, 
            "identifier": "Tołstoja 3"
            }
        ]


def test_get_one_flat(client, sample_data):
    response = client.get('/api/v1/flats/1')
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == 'Mostnika 5'
    assert response_data['data']['address'] == 'Mostnika 5/12 01-100 Słupsk'
    assert response_data['data']['description'] == 'Mieszkanie dwupokojowe z aneksem kuchennym na trzecim piętrze.'
    assert response_data['data']['landlord']['identifier'] == 'landlord1'
    assert response_data['data']['landlord']['first_name'] == 'Jan'
    assert response_data['data']['landlord']['last_name'] == 'Kowalski'


def test_get_all_landlord_flats(client, sample_data):
    response = client.get('/api/v1/landlords/2/flats')
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True  
    assert response_data['number_of_records'] == 2
    assert len(response_data['data']) == 2


def test_create_flat(client, landlord, flat_data, landlord_token):
    response = client.post('/api/v1/flats', 
                        json=flat_data,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == flat_data['identifier']
    assert response_data['data']['address'] == flat_data['address']
    assert response_data['data']['status'] == 'active'
    assert response_data['data']['landlord']['identifier'] == landlord['identifier']
    assert response_data['data']['landlord']['first_name'] == landlord['first_name']
    assert response_data['data']['landlord']['last_name'] == landlord['last_name']


@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'identifier': 'newidentifier'}, 'address'),
        ({'address': 'newaddress'}, 'identifier'),
    ]
)
def test_create_flat_missing_data(client, landlord_token, 
                                    data, missing_field):
    response = client.post('/api/v1/flats', 
                        json=data,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_update_flat(client, landlord_token, landlord, flat_data):
    response = client.post('/api/v1/flats', 
                            json=flat_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    assert response.get_json()['data']['id'] == 1

    updated_flat = {
        "identifier": "updatediflat",
        "address": "updated address",
        "description": "updated description",
        "status": "inactive"
    }

    response = client.put('/api/v1/flats/1',
                            json=updated_flat,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == updated_flat['identifier']
    assert response_data['data']['address'] == updated_flat['address']
    assert response_data['data']['status'] == updated_flat['status']
    assert response_data['data']['description'] == updated_flat['description']
    assert response_data['data']['landlord']['identifier'] == landlord['identifier']
    assert response_data['data']['landlord']['first_name'] == landlord['first_name']
    assert response_data['data']['landlord']['last_name'] == landlord['last_name']


@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'identifier': 'updatedflat'}, 'address'),
        ({'address': 'updatedaddress'}, 'identifier')
    ]
)
def test_update_flat_missing_data(client, landlord_token, flat_data,
                                    data, missing_field):
    response = client.post('/api/v1/flats', 
                            json=flat_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    assert response.get_json()['data']['id'] == 1


    response = client.put('/api/v1/flats/1',
                            json=data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_update_flat_wrong_status(client, landlord_token, flat_data):
    response = client.post('/api/v1/flats', 
                            json=flat_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    assert response.get_json()['data']['id'] == 1

    updated_flat = {
        "identifier": "updatediflat",
        "address": "updated address",
        "description": "updated description",
        "status": "wrong_status"
    }

    response = client.put('/api/v1/flats/1',
                            json=updated_flat,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert response_data['message'] == 'Allowed statuses: active, inactive, sold'


def test_update_flat_existing_identifier(client, landlord_token, flat_data, flat_2_data):
    response = client.post('/api/v1/flats', 
                            json=flat_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    assert response.get_json()['data']['id'] == 1

    response = client.post('/api/v1/flats', 
                            json=flat_2_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    assert response.get_json()['data']['id'] == 2    

    updated_flat = {
        "identifier": flat_data['identifier'],
        "address": "updated address",
        "description": "updated description"
    }

    response = client.put('/api/v1/flats/2',
                            json=updated_flat,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False

    description = f'Flat with identifier {updated_flat["identifier"]} already exists'
    assert response_data['message'] == description


def test_delete_flat(client, landlord_token, flat_data):
    response = client.post('/api/v1/flats', 
                            json=flat_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    flat_id = response.get_json()['data']['id'] 
    assert flat_id == 1

    response = client.delete('/api/v1/flats/1',
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data'] == f'Flat with id {flat_id} has been deleted'


def test_delete_flat_missing_token(client, landlord_token, flat_data):
    response = client.post('/api/v1/flats', 
                            json=flat_data,
                            headers={
                                'Authorization': f'Bearer {landlord_token}'
                            })
    
    flat_id = response.get_json()['data']['id'] 
    assert flat_id == 1

    response = client.delete('/api/v1/flats/1')
    response_data = response.get_json()

    print(response_data)
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    alert = 'Missing landlord token. Please login or register as landlord.'
    assert alert in response_data['message']
