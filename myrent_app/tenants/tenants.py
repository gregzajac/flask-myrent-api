from flask import jsonify, abort
from webargs.flaskparser import use_args
from myrent_app import db
from myrent_app.tenants import tenants_bp
from myrent_app.models import Tenant, TenantSchema, tenant_schema, \
                            tenant_update_password_schema
from myrent_app.utils import token_landlord_required, token_landlord_tenant_required, \
                            validate_json_content_type, generate_hashed_password


@tenants_bp.route('/tenants', methods=['GET'])
@token_landlord_required
def get_landlord_tenants(landlord_id: int):
    tenants = Tenant.query.filter(Tenant.landlord_id == landlord_id).all()
    items = TenantSchema(many=True, exclude=['landlord']).dump(tenants)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })


@tenants_bp.route('/tenants/<int:tenant_id>', methods=['GET'])
@token_landlord_required
def get_landlord_tenant(landlord_id: int, tenant_id: int):
    tenant = Tenant.query.filter(Tenant.landlord_id == landlord_id) \
                        .filter(Tenant.id == tenant_id).first()
    if tenant is None:
        abort(404, description=f'Tenant with id {tenant_id} not found')

    return jsonify({
        'success': True,
        'data': tenant_schema.dump(tenant)
    })


@tenants_bp.route('/tenants', methods=['POST'])
@token_landlord_required
@validate_json_content_type
@use_args(TenantSchema(exclude=['landlord_id']), error_status_code=400)
def create_tenant(landlord_id: int, args: dict):
    if Tenant.query.filter(Tenant.identifier == args['identifier']).first():
        abort(409, description=f'Tenant with identifier {args["identifier"]} already exists')

    if Tenant.query.filter(Tenant.email == args['email']).first():
        abort(409, description=f'Tenant with email {args["email"]} already exists') 
    
    args['password'] = generate_hashed_password(args['password'])
    
    new_tenant = Tenant(landlord_id=landlord_id, **args)
    db.session.add(new_tenant)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': tenant_schema.dump(new_tenant)
    }), 201


@tenants_bp.route('/tenants/login', methods=['POST'])
@validate_json_content_type
@use_args(TenantSchema(only=['identifier', 'password']), error_status_code=400)
def login_tenant(args: dict):
    tenant = Tenant.query.filter(Tenant.identifier == args['identifier']).first()

    if not tenant:
        abort(401, description='Invalid credentials')

    if not tenant.is_password_valid(args['password']):
        abort(401, description='Invalid credentials')

    token = tenant.generate_jwt()

    return jsonify({
        'success': True,
        'token': token.decode()
    })


@tenants_bp.route('/tenants/me', methods=['GET'])
@token_landlord_tenant_required
def get_current_tenant(id_model_tuple: tuple):
    if id_model_tuple[1] != 'tenants':
        abort(404, description='Invalid token. Please login or register as tenant.')

    tenant = Tenant.query.get_or_404(id_model_tuple[0],
                            description=f'Tenant with id {id_model_tuple[0]} not found')

    return jsonify({
        'success': True,
        'data': tenant_schema.dump(tenant)
    })


@tenants_bp.route('/tenants/<int:tenant_id>/password', methods=['PUT'])
@token_landlord_tenant_required
@validate_json_content_type
@use_args(tenant_update_password_schema, error_status_code=400)
def update_tenant_password(id_model_tuple: tuple, args: dict, tenant_id: int):
    if id_model_tuple[1] == 'landlords':
        tenant = Tenant.query.filter(Tenant.landlord_id == id_model_tuple[0]) \
                            .filter(Tenant.id == tenant_id).first()
        if tenant is None:
            abort(404, description=f'Tenant with id {tenant_id} not found')

    if id_model_tuple[1] == 'tenants':
        if id_model_tuple[0] != tenant_id:
            abort(404, description=f'Incorrect tenant id')
        tenant = Tenant.query.get_or_404(tenant_id, 
                                        description=f'Tenant with id {tenant_id} not found')

    if not tenant.is_password_valid(args['current_password']):
        abort(401, description='Invalid password')

    tenant.password = generate_hashed_password(args['new_password'])
    db.session.commit()

    return jsonify({
        'success': True,
        'data': tenant_schema.dump(tenant)
    })


@tenants_bp.route('/tenants/<int:tenant_id>/data', methods=['PUT'])
@token_landlord_tenant_required
@validate_json_content_type
@use_args(TenantSchema(exclude=['password']), error_status_code=400)
def update_tenant_data(id_model_tuple: tuple, args: dict, tenant_id: int):
    if id_model_tuple[1] == 'landlords':
        tenant = Tenant.query.filter(Tenant.landlord_id == id_model_tuple[0]) \
                                .filter(Tenant.id == tenant_id).first()
        if tenant is None:
            abort(404, description=f'Tenant with id {tenant_id} not found')

    if id_model_tuple[1] == 'tenants':
        if id_model_tuple[0] != tenant_id:
            abort(404, description=f'Incorrect tenant id')
        tenant = Tenant.query.get_or_404(tenant_id, 
                                description=f'Tenant with id {tenant_id} not found')

    tenant_with_this_identifier = Tenant.query.filter(
                                        Tenant.identifier == args['identifier']).first()
    if tenant_with_this_identifier is not None and \
        tenant_with_this_identifier.identifier != tenant.identifier:
            abort(409, description=f'Tenant with identifier {args["identifier"]}'
                                    ' already exists')
          
    tenant_with_this_email = Tenant.query.filter(
                                    Tenant.email == args['email']).first()
    if tenant_with_this_email is not None and \
        tenant_with_this_email.email != tenant.email:
            abort(409, description=f'Tenant with email {args["email"]}'
                                    ' already exists')
           
    tenant.identifier = args['identifier']
    tenant.email = args['email']
    tenant.first_name = args['first_name']
    tenant.last_name = args['last_name']
    tenant.phone = args['phone']
    tenant.address = args['address']
    description = args.get('description')
    if description is not None:
        tenant.description = description
    db.session.commit()

    return jsonify({
        'success': True,
        'data': tenant_schema.dump(tenant)
    })


@tenants_bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
@token_landlord_required
def delete_tenant(landlord_id: int, tenant_id: int):
    tenant = Tenant.query.get_or_404(tenant_id, 
                            description=f'Tenant with id {tenant_id} not found')

    if tenant.landlord_id != landlord_id:
        abort(404, description=f'Tenant with id {tenant_id} not found')

    db.session.delete(tenant)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Tenant with id {tenant_id} has been deleted'
    })
