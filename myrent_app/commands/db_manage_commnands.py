import os, json
from shutil import copyfile
from datetime import datetime

from config import base_dir
from myrent_app import db
from myrent_app.commands import db_manage_bp
from myrent_app.models import Landlord, Flat, Tenant, Agreement, \
                                Settlement, Picture
from myrent_app.utils import generate_hashed_password


PICTURES_LIST = ['example.JPG', 'example2.JPG', 'example3.JPG']

def load_json_data(filename: str) -> list:
    json_path = os.path.join(base_dir, 'samples', filename)
    with open(json_path, encoding='utf-8') as file:
        data_json = json.load(file)
    return data_json

def load_picture_data(flat_id: int, filename: str, description: str) -> dict:
    return {
        'name': filename,
        'description': description,
        'path': os.path.join(base_dir, 'uploads', filename),
        'flat_id': flat_id
    }


@db_manage_bp.cli.group()
def db_manage():
    """Database management commands"""
    pass


@db_manage.command()
def add_data():
    """Add sample data to the database"""
    try:
        data_json = load_json_data('landlords.json')
        for item in data_json:
            item['password'] = generate_hashed_password(item['password'])
            landlord = Landlord(**item)
            db.session.add(landlord)

        data_json = load_json_data('flats.json')
        for item in data_json:
            flat = Flat(**item)
            db.session.add(flat)        
            
        data_json = load_json_data('tenants.json')
        for item in data_json:
            item['password'] = generate_hashed_password(item['password'])
            tenant = Tenant(**item)
            db.session.add(tenant)

        data_json = load_json_data('agreements.json')
        for item in data_json:
            item['sign_date'] = datetime.strptime(item['sign_date'], '%d-%m-%Y').date()
            item['date_from'] = datetime.strptime(item['date_from'], '%d-%m-%Y').date()
            item['date_to'] = datetime.strptime(item['date_to'], '%d-%m-%Y').date()
            agreement = Agreement(**item)
            db.session.add(agreement)

        data_json = load_json_data('settlements.json')
        for item in data_json:
            item['date'] = datetime.strptime(item['date'], '%d-%m-%Y').date()
            settlement = Settlement(**item)
            db.session.add(settlement)

        flat_id = 0
        for picture_name in PICTURES_LIST:
            flat_id += 1
            item = load_picture_data(flat_id, picture_name, f'Opis dla fotki {picture_name}')
            picture = Picture(**item)
            db.session.add(picture)
            copyfile(os.path.join(base_dir, 'samples', picture_name), item['path'])
        
        db.session.commit()
        print('Data has been added to database')
    except Exception as exc:
        print(f'Unexpected error: {exc}')


@db_manage.command()
def remove_data():
    """Remove all data from the database"""
    try:
        db.session.execute('DELETE FROM pictures')
        db.session.execute('ALTER TABLE pictures AUTO_INCREMENT=1')
        db.session.execute('DELETE FROM settlements')
        db.session.execute('ALTER TABLE settlements AUTO_INCREMENT=1')        
        db.session.execute('DELETE FROM agreements')
        db.session.execute('ALTER TABLE agreements AUTO_INCREMENT=1')        
        db.session.execute('DELETE FROM flats')
        db.session.execute('ALTER TABLE flats AUTO_INCREMENT=1')        
        db.session.execute('DELETE FROM tenants')
        db.session.execute('ALTER TABLE tenants AUTO_INCREMENT=1')
        db.session.execute('DELETE FROM landlords')
        db.session.execute('ALTER TABLE landlords AUTO_INCREMENT=1')

        for file in os.listdir(os.path.join(base_dir, 'uploads')):
            os.remove(os.path.join(base_dir, 'uploads', file))

        print('All data has been deleted') 
    except Exception as exc:
        print(f'Unexpected error: {exc}')
