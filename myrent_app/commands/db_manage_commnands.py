import os, json, boto3, mimetypes
# from shutil import copyfile
from datetime import datetime
from flask import current_app

# from config import base_dir
from myrent_app import db
from myrent_app.commands import db_manage_bp
from myrent_app.models import Landlord, Flat, Tenant, Agreement, \
                            Settlement, Picture
from myrent_app.utils import generate_hashed_password, upload_file_to_s3, \
                            delete_all_files_from_s3, allowed_picture


def load_json_data(filename: str) -> list:
    json_path = os.path.join(current_app.config['SAMPLES_FOLDER'], filename)
    with open(json_path, encoding='utf-8') as file:
        data_json = json.load(file)
    return data_json

def get_picture_samples():
    result = []
    for file in os.listdir(current_app.config['SAMPLES_FOLDER']):
        if allowed_picture(file):
            result.append(os.path.join(current_app.config['SAMPLES_FOLDER'], file))
    return result


@db_manage_bp.cli.group()
def db_manage():
    """Database management commands"""
    pass


@db_manage.command()
def add_data():
    """Add sample data to the database and AWS S3"""
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

        pictures_list = get_picture_samples()
        if pictures_list:
            bucket_name = current_app.config.get('S3_BUCKET')
            flat_id = 0

            s3 = boto3.client('s3',
                        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
                        )

            for pic in pictures_list:
                flat_id += 1
                file_name = f'flat{flat_id}_{os.path.split(pic)[1]}'
                file_type = mimetypes.guess_type(pic)[0]

                s3.upload_file(pic, 
                            bucket_name, 
                            file_name, 
                            ExtraArgs={
                                'ACL': 'public-read',
                                'ContentType': file_type
                            })
                print(f'Uploading file {file_name} to s3 bucket {bucket_name}')

                picture = Picture(name=file_name,
                                description=f'Description for {file_name}',
                                path=f'http://{bucket_name}.s3.amazonaws.com/{file_name}',
                                flat_id=flat_id)
                db.session.add(picture)
        
        db.session.commit()
        print('Data has been added to database')
    except Exception as exc:
        print(f'Unexpected error: {exc}')


@db_manage.command()
def remove_data_mysql():
    """Remove all data from the MySQL database and from AWS S3"""
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
        db.session.commit()

        print('All data has been deleted from database') 

        result_info = delete_all_files_from_s3(current_app.config['S3_BUCKET'],
                                            current_app.config['AWS_ACCESS_KEY_ID'],
                                            current_app.config['AWS_SECRET_ACCESS_KEY'])
        print(result_info)

    except Exception as exc:
        print(f'Unexpected error: {exc}')


@db_manage.command()
def remove_data_postgres():
    """Remove all data from the database and from AWS S3"""
    try:
        db.session.execute('DELETE FROM pictures;')
        db.session.execute('ALTER SEQUENCE pictures_id_seq RESTART WITH 1;')
        db.session.execute('DELETE FROM settlements;')
        db.session.execute('ALTER SEQUENCE settlements_id_seq RESTART WITH 1;')
        db.session.execute('DELETE FROM agreements;')
        db.session.execute('ALTER SEQUENCE agreements_id_seq RESTART WITH 1;')
        db.session.execute('DELETE FROM flats;')
        db.session.execute('ALTER SEQUENCE flats_id_seq RESTART WITH 1;')
        db.session.execute('DELETE FROM tenants;')
        db.session.execute('ALTER SEQUENCE tenants_id_seq RESTART WITH 1;')
        db.session.execute('DELETE FROM landlords;')
        db.session.execute('ALTER SEQUENCE landlords_id_seq RESTART WITH 1;')
        db.session.commit()

        print('All data has been deleted from database')

        result_info = delete_all_files_from_s3(current_app.config['S3_BUCKET'],
                                            current_app.config['AWS_ACCESS_KEY_ID'],
                                            current_app.config['AWS_SECRET_ACCESS_KEY'])
        print(result_info)

    except Exception as exc:
        print(f'Unexpected error: {exc}')
