import pytest
import os
from myrent_app import create_app, db
from config import base_dir
from myrent_app.commands.db_manage_commnands import add_data


@pytest.fixture
def app():
    app = create_app('testing')

    with app.app_context():
        db.create_all()

    yield app
    app.config['DB_FILE_PATH'].unlink()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def landlord(client):
    landlord = {
        "address": "testaddress", 
        "description": "testdescription", 
        "email": "testmail@wp.pl", 
        "first_name": "testfirst_name", 
        "identifier": "testidentifier", 
        "last_name": "testlast_name",
        "phone": "testphone",
        "password": "testpassword"
    }

    client.post('/api/v1/landlords/register', 
                json=landlord)
    return landlord


@pytest.fixture
def landlord_token(client, landlord):
    response = client.post('/api/v1/landlords/login', 
                            json={
                                'identifier': landlord['identifier'],
                                'password': landlord['password']
                            })
    response_data = response.get_json()
    return response_data['token']
  

@pytest.fixture
def sample_data(app):
    runner = app.test_cli_runner()
    runner.invoke(add_data)


@pytest.fixture
def flat_data():
    return {
        'identifier': 'testidentifier',
        'address': 'testaddress',
        'description': 'testdescription'
    }


@pytest.fixture
def flat(client, landlord_token):
    flat = {
        'identifier': 'testidentifier',
        'address': 'testaddress',
        'description': 'testdescription'        
    }

    client.post('/api/v1/flats',
                json=flat,
                headers={
                    'Authorization': f'Bearer {landlord_token}'
                })
    return flat


@pytest.fixture
def flat_2_data():
    return {
        'identifier': 'testidentifier2',
        'address': 'testaddress2',
        'description': 'testdescription2'
    }

@pytest.fixture
def tenant(client, landlord_token):
    tenant = {
        "address": "testaddress",
        "description": "testtenantdescription",
        "email": "testtenantmail@wp.pl",
        "first_name": "testfirst_name",
        "identifier": "testtenant",
        "last_name": "testlast_name",
        "phone": "testphone",
        "password": "testtenant"
    }

    client.post('/api/v1/tenants', 
                json=tenant,
                headers={
                    'Authorization': f'Bearer {landlord_token}'
                })

    return tenant

@pytest.fixture
def tenant_token(client, tenant):
    print('tenant dane: ', tenant)
    response = client.post('/api/v1/tenants/login', 
                            json={
                                'identifier': tenant['identifier'],
                                'password': tenant['password']
                            })
    response_data = response.get_json()
    print('dane response data tenant_token: ', response_data)
    return response_data['token']

@pytest.fixture
def tenant2(client, landlord_token):
    tenant2 = {
        "address": "testaddress2",
        "description": "testtenantdescription2",
        "email": "testtenantmail2@wp.pl",
        "first_name": "testfirst_name2",
        "identifier": "testtenant2",
        "last_name": "testlast_name2",
        "phone": "testphone2",
        "password": "testtenant2"
    }

    client.post('/api/v1/tenants', 
                json=tenant2,
                headers={
                    'Authorization': f'Bearer {landlord_token}'
                })

    return tenant2

@pytest.fixture
def tenant2_token(client, tenant2):
    response = client.post('/api/v1/tenants/login', 
                            json={
                                'identifier': tenant2['identifier'],
                                'password': tenant2['password']
                            })
    response_data = response.get_json()

    return response_data['token']

@pytest.fixture
def agreement_data():
    return {
        "identifier": "testagreement",
        "sign_date": "01-01-2020",
        "date_from": "01-01-2020",
        "date_to": "30-06-2022",
        "price_value": 3000,
        "price_period": "month",
        "payment_deadline": 10,
        "deposit_value": 7000,
        "description": "testdescription"
    }

@pytest.fixture
def agreement(client, flat, tenant, agreement_data, landlord_token):
    client.post('/api/v1/flats/1/tenants/1/agreements', 
                json=agreement_data,
                headers={
                    'Authorization': f'Bearer {landlord_token}'
                })
    return agreement_data


@pytest.fixture
def file_example():
    file_example = {
        'name': 'example.JPG',
        'source': os.path.join(base_dir, 'samples', 'example.JPG'),
        'path': os.path.join(base_dir, 'tests', 'uploads', 'example.JPG'),
        'description': 'picture description'
    }
    return file_example
