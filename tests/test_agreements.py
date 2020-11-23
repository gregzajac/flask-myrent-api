import pytest


def test_get_agreements_no_token(client):
    response = client.get('/api/v1/agreements')
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data['success'] is False
    assert response_data['message'] == 'Missing token. Please login or register.' 


def test_get_agreements_no_records(client, landlord_token):
    response = client.get('/api/v1/agreements', 
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert response_data['data'] == [] 
    assert response_data['number_of_records'] == 0


def test_get_agreements_landlord_token(client, sample_data):
    response = client.post('/api/v1/landlords/login',
                        json={
                            'identifier': 'landlord2',
                            'password': 'haslo2'
                        })
    
    token = response.get_json()['token']

    assert token

    response = client.get('/api/v1/agreements', 
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert len(response_data['data']) == 2 
    assert response_data['number_of_records'] == 2


def test_get_agreements_tenant_token(client, sample_data):
    response = client.post('/api/v1/tenants/login',
                        json={
                            'identifier': 'tenant2',
                            'password': 'haslo2'
                        })
    token = response.get_json()['token']

    assert token
    
    response = client.get('/api/v1/agreements', 
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert len(response_data['data']) == 1 
    assert response_data['number_of_records'] == 1


def test_get_agreement_no_token(client):
    response = client.get('/api/v1/agreements/1')
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data['success'] is False
    assert response_data['message'] == 'Missing token. Please login or register.'     


def test_get_agreement_landlord_token(client, sample_data):
    response = client.post('/api/v1/landlords/login',
                        json={
                            'identifier': 'landlord1',
                            'password': 'haslo1'
                        })
    token = response.get_json()['token']

    assert token

    response = client.get('/api/v1/agreements/1', 
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == 'Umowa1'
    assert len(response_data['data']) == 14
 

def test_get_agreement_other_landlord(client, sample_data):
    response = client.post('/api/v1/landlords/login',
                        json={
                            'identifier': 'landlord2',
                            'password': 'haslo2'
                        })
    token = response.get_json()['token']

    assert token

    response = client.get('/api/v1/agreements/1', 
                        headers={
                            'Authorization': f'Bearer {token}'
                        })                    
    response_data = response.get_json()

    assert response.status_code == 404
    assert response_data['success'] is False
    assert response_data['message'] == 'Agreement with id 1 not found'


def test_get_agreement_tenant_token(client, sample_data):
    response = client.post('/api/v1/tenants/login',
                        json={
                            'identifier': 'tenant1',
                            'password': 'haslo1'
                        })
    token = response.get_json()['token']

    assert token

    response = client.get('/api/v1/agreements/1', 
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == 'Umowa1'
    assert len(response_data['data']) == 14


def test_get_agreement_other_tenant(client, sample_data):
    response = client.post('/api/v1/tenants/login',
                        json={
                            'identifier': 'tenant2',
                            'password': 'haslo2'
                        })
    token = response.get_json()['token']

    assert token

    response = client.get('/api/v1/agreements/1', 
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 404
    assert response_data['success'] is False
    assert response_data['message'] == 'Agreement with id 1 not found'


def test_create_agreement(client, tenant, flat_data, agreement_data, landlord_token):
    response = client.post('/api/v1/flats',
                        json=flat_data,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response_data['data']['id'] == 1

    response = client.post('/api/v1/flats/1/tenants/1/agreements',
                        json=agreement_data,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['identifier'] == agreement_data['identifier']
    assert response_data['data']['sign_date'] == agreement_data['sign_date']
    assert response_data['data']['date_from'] == agreement_data['date_from']
    assert response_data['data']['date_to'] == agreement_data['date_to']
    assert response_data['data']['price_value'] == agreement_data['price_value']
    assert response_data['data']['price_period'] == agreement_data['price_period']
    assert response_data['data']['payment_deadline'] == agreement_data['payment_deadline']
    assert response_data['data']['deposit_value'] == agreement_data['deposit_value']
    assert response_data['data']['description'] == agreement_data['description']
    assert response_data['data']['flat'] == {
                                            'id': 1,
                                            'identifier': flat_data['identifier'],
                                            'address': flat_data['address']
                                        }
    assert response_data['data']['tenant'] == {
                                            'id': 1,
                                            'identifier': tenant['identifier'],
                                            'first_name': tenant['first_name'],
                                            'last_name': tenant['last_name']
                                        }


def test_create_agreement_no_token(client, tenant, flat_data, agreement_data, 
                                    landlord_token):
    response = client.post('/api/v1/flats',
                        json=flat_data,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response_data['data']['id'] == 1

    response = client.post('/api/v1/flats/1/tenants/1/agreements', json=agreement_data)
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data['success'] is False
    assert response.headers['Content-Type'] == 'application/json'
    alert = 'Missing landlord token. Please login or register as landlord.'
    assert response_data['message'] == alert


def test_create_agreement_tenant_token(client, tenant, flat_data, agreement_data, 
                                    landlord_token, tenant_token):
    response = client.post('/api/v1/flats',
                        json=flat_data,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response_data['data']['id'] == 1

    response = client.post('/api/v1/flats/1/tenants/1/agreements', 
                        json=agreement_data,
                        headers={
                            'Authorization': f'Bearer {tenant_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data['success'] is False
    alert = 'Only landlord functionality'
    assert response_data['message'] == alert


def test_create_agreement_wrong_flat(client, sample_data, agreement_data):
    response = client.post('/api/v1/landlords/login',
                        json={
                            'identifier': 'landlord1',
                            'password': 'haslo1'
                        })
    token = response.get_json()['token']

    assert token

    response = client.post('/api/v1/flats/2/tenants/1/agreements',
                        json=agreement_data,
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 404
    assert response_data['success'] is False
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['message'] == 'Flat with id 2 not found'


def test_create_agreement_wrong_tenant(client, sample_data, agreement_data):
    response = client.post('/api/v1/landlords/login',
                        json={
                            'identifier': 'landlord1',
                            'password': 'haslo1'
                        })
    token = response.get_json()['token']

    assert token

    response = client.post('/api/v1/flats/1/tenants/2/agreements',
                        json=agreement_data,
                        headers={
                            'Authorization': f'Bearer {token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 404
    assert response_data['success'] is False
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['message'] == 'Tenant with id 2 not found'


def test_update_agreement(client, flat, tenant, agreement, landlord_token):
    updated_agreement = {
        "identifier": "updatedagreement",
        "sign_date": "01-02-2020",
        "date_from": "01-02-2020",
        "date_to": "30-06-2022",
        "price_value": 3001,
        "price_period": "month",
        "payment_deadline": 8,
        "deposit_value": 1,
        "description": "testupdateddescription"
    }

    response = client.put('/api/v1/agreements/1', 
                        json=updated_agreement,
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['data']['identifier'] == updated_agreement['identifier']
    assert response_data['data']['sign_date'] == updated_agreement['sign_date']
    assert response_data['data']['date_from'] == updated_agreement['date_from']
    assert response_data['data']['date_to'] == updated_agreement['date_to']
    assert response_data['data']['price_value'] == updated_agreement['price_value']
    assert response_data['data']['price_period'] == updated_agreement['price_period']
    assert response_data['data']['payment_deadline'] == updated_agreement['payment_deadline']
    assert response_data['data']['deposit_value'] == updated_agreement['deposit_value']
    assert response_data['data']['description'] == updated_agreement['description']
    assert response_data['data']['flat'] == {
                                            'id': 1,
                                            'identifier': flat['identifier'],
                                            'address': flat['address']
                                        }
    assert response_data['data']['tenant'] == {
                                            'id': 1,
                                            'identifier': tenant['identifier'],
                                            'first_name': tenant['first_name'],
                                            'last_name': tenant['last_name']
                                        }


def test_update_agreement_no_token(client, flat, tenant, agreement):
    updated_agreement = {
        "identifier": "updatedagreement",
        "sign_date": "01-02-2020",
        "date_from": "01-02-2020",
        "date_to": "30-06-2022",
        "price_value": 3001,
        "price_period": "month",
        "payment_deadline": 8,
        "deposit_value": 1,
        "description": "testupdateddescription"
    }

    response = client.put('/api/v1/agreements/1', json=updated_agreement)
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data['success'] is False
    assert response.headers['Content-Type'] == 'application/json'
    alert = 'Missing landlord token. Please login or register as landlord.'
    assert response_data['message'] == alert


def test_update_agreement_tenant_token(client, flat, tenant, agreement, tenant_token):
    updated_agreement = {
        "identifier": "updatedagreement",
        "sign_date": "01-02-2020",
        "date_from": "01-02-2020",
        "date_to": "30-06-2022",
        "price_value": 3001,
        "price_period": "month",
        "payment_deadline": 8,
        "deposit_value": 1,
        "description": "testupdateddescription"
    }

    response = client.put('/api/v1/agreements/1', 
                        json=updated_agreement,
                        headers={
                            'Authorization': f'Bearer {tenant_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 401
    assert response_data['success'] is False
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['message'] == 'Only landlord functionality'


def test_delete_agreement(client, agreement, landlord_token):
    response = client.delete('/api/v1/agreements/1',
                        headers={
                            'Authorization': f'Bearer {landlord_token}'
                        })
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['success'] is True
    assert response_data['data'] == 'Agreement with id 1 has been deleted'
