from flask import jsonify, abort, request
# from flask_cors import cross_origin
from webargs.flaskparser import use_args
from pathlib import Path

from myrent_app import db
from myrent_app.landlords import landlords_bp
from myrent_app.models import Landlord, LandlordSchema, landlord_schema, \
    landlord_update_password_schema
from myrent_app.utils import validate_json_content_type, token_landlord_required, \
    get_schema_args, apply_order, apply_filter, get_pagination, generate_hashed_password


@landlords_bp.route('/landlords', methods=['GET'])
# @cross_origin
def get_all_landlords():
    query = Landlord.query
    query = apply_order(Landlord, query)
    query = apply_filter(Landlord, query)
    items, pagination = get_pagination(query, 'landlords.get_all_landlords')
    schema_args = get_schema_args(Landlord)
    landlords = LandlordSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': landlords,
        'number_of_records': len(landlords),
        'pagination': pagination
    })


@landlords_bp.route('/landlords/<int:landlord_id>', methods=['GET'])
def get_one_landlord(landlord_id: int):
    landlord = Landlord.query.get_or_404(landlord_id, 
                    description=f'Landlord with id {landlord_id} not found')

    return jsonify({
        'success': True,
        'data': landlord_schema.dump(landlord)
    })


@landlords_bp.route('/landlords/register', methods=['POST'])
@validate_json_content_type
@use_args(landlord_schema, error_status_code=400)
def register_landlord(args: dict):
    if Landlord.query.filter(Landlord.identifier == args['identifier']).first():
        abort(409, description=f'Landlord with identifier {args["identifier"]} already exists')

    if Landlord.query.filter(Landlord.email == args['email']).first():
        abort(409, description=f'Landlord with email {args["email"]} already exists') 
    
    args['password'] = generate_hashed_password(args['password'])
    
    new_landlord = Landlord(**args)
    db.session.add(new_landlord)
    db.session.commit()

    token = new_landlord.generate_jwt()

    return jsonify({
        'success': True,
        'token': token.decode()
    }), 201


@landlords_bp.route('/landlords/login', methods=['POST'])
@validate_json_content_type
@use_args(LandlordSchema(only=['identifier', 'password']), error_status_code=400)
def login_landlord(args: dict):
    landlord = Landlord.query.filter(Landlord.identifier == args['identifier']).first()

    if not landlord:
        abort(401, description='Invalid credentials')

    if not landlord.is_password_valid(args['password']):
        abort(401, description='Invalid credentials')

    token = landlord.generate_jwt()

    return jsonify({
        'success': True,
        'token': token.decode()
    })


@landlords_bp.route('/landlords/me', methods=['GET'])
@token_landlord_required
def get_current_landlord(landlord_id: str):
    landlord = Landlord.query.get_or_404(landlord_id, 
                    description=f'Landlord with id {landlord_id} not found')

    return jsonify({
        'success': True,
        'data': landlord_schema.dump(landlord)
    })  


@landlords_bp.route('/landlords/password', methods=['PUT'])
@validate_json_content_type
@token_landlord_required
@use_args(landlord_update_password_schema, error_status_code=400)
def update_landlord_password(landlord_id: str, args: dict):
    landlord = Landlord.query.get_or_404(landlord_id, 
                    description=f'Landlord with id {landlord_id} not found')

    if not landlord.is_password_valid(args['current_password']):
        abort(401, description='Invalid password')

    landlord.password = generate_hashed_password(args['new_password'])
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': landlord_schema.dump(landlord)
    })
  
 
@landlords_bp.route('/landlords/data', methods=['PUT'])
@validate_json_content_type
@token_landlord_required
@use_args(LandlordSchema(exclude=['password']), error_status_code=400)
def update_landlord_data(landlord_id: int, args: dict):
    landlord = Landlord.query.get_or_404(landlord_id, 
                    description=f'Landlord with id {landlord_id} not found')

    landlord_with_this_identifier = Landlord.query.filter(
                                        Landlord.identifier == args['identifier']).first()
    if landlord_with_this_identifier is not None and \
        landlord_with_this_identifier.identifier != landlord.identifier:
            abort(409, description=f'Landlord with identifier {args["identifier"]}'
                                    ' already exists')
          
    landlord_with_this_email = Landlord.query.filter(
                                    Landlord.email == args['email']).first()
    if landlord_with_this_email is not None and \
        landlord_with_this_email.email != landlord.email:
            abort(409, description=f'Landlord with email {args["email"]}'
                                    ' already exists')
           
    landlord.identifier = args['identifier']
    landlord.email = args['email']
    landlord.first_name = args['first_name']
    landlord.last_name = args['last_name']
    landlord.phone = args['phone']
    landlord.address = args['address']
    description = args.get('description')
    if description is not None:
        landlord.description = description
    db.session.commit()

    return jsonify({
        'success': True,
        'data': landlord_schema.dump(landlord)
    })

