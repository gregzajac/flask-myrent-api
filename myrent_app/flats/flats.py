from flask import jsonify, abort
from webargs.flaskparser import use_args

from myrent_app import db
from myrent_app.flats import flats_bp
from myrent_app.models import Flat, FlatSchema, flat_schema, Landlord
from myrent_app.utils import apply_order, apply_filter, get_pagination, validate_json_content_type, get_schema_args, token_landlord_required


@flats_bp.route('/flats', methods=['GET'])
def get_all_flats():
    query = Flat.query
    query = apply_order(Flat, query)
    query = apply_filter(Flat, query)
    items, pagination = get_pagination(query, 'flats.get_all_flats')
    
    schema_args = get_schema_args(Flat)
    flats = FlatSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': flats,
        'number_of_records': len(flats),
        'pagination': pagination
    })


@flats_bp.route('/flats/<int:flat_id>', methods=['GET'])
def get_one_flat(flat_id: str):
    flat = Flat.query.get_or_404(flat_id, description=f'Flat with id {flat_id} not found')

    return jsonify({
        'success': True,
        'data': flat_schema.dump(flat)
    })


@flats_bp.route('/landlords/<int:landlord_id>/flats', methods=['GET'])
def get_all_landlord_flats(landlord_id: str):
    Landlord.query.get_or_404(landlord_id, 
                            description=f'Landlord with id {landlord_id} not found')
    flats = Flat.query.filter(Flat.landlord_id == landlord_id).all()
    items = FlatSchema(many=True, exclude=['landlord']).dump(flats)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })



@flats_bp.route('/flats', methods=['POST'])
@token_landlord_required
@validate_json_content_type
@use_args(FlatSchema(exclude=['landlord_id']), error_status_code=400)
def create_flat(landlord_id: int, args: dict):
    flat_identifier = Flat.query.filter(Flat.identifier == args['identifier']).first()
    if flat_identifier is not None:
        abort(409, description=f'Flat with identifier {args["identifier"]} already exists')
    
    flat = Flat(landlord_id=landlord_id, **args)
    db.session.add(flat)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': flat_schema.dump(flat)
    }), 201


@flats_bp.route('/flats/<int:flat_id>', methods=['PUT'])
@token_landlord_required
@validate_json_content_type
@use_args(FlatSchema(exclude=['landlord_id']), error_status_code=400)
def update_flat(landlord_id: int, args: dict, flat_id: int):
    flat = Flat.query.get_or_404(flat_id, 
                                description=f'Flat with id {flat_id} not found')
    
    flat_with_this_identifier = Flat.query.filter(
                                                Flat.identifier == args['identifier']
                                            ).first()
    if flat_with_this_identifier is not None and \
        flat_with_this_identifier.identifier != flat.identifier:
        abort(409, description=f'Flat with identifier {args["identifier"]} already exists')

    status = args.get('status')
    if status is not None:
        if status not in ['active', 'inactive', 'sold']:
            abort(409, description='Allowed statuses: active, inactive, sold')
        flat.status = status

    description = args.get('description')
    if description is not None:
        flat.description = description

    flat.identifier = args['identifier']
    flat.address = args['address']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': flat_schema.dump(flat)
    })


@flats_bp.route('/flats/<int:flat_id>', methods=['DELETE'])
@token_landlord_required
def delete_flat(landlord_id: int, flat_id):
    flat = Flat.query.get_or_404(flat_id, 
                                description=f'Flat with id {flat_id} not found')

    if flat.landlord_id != landlord_id:
        abort(404, description=f'Flat with id {flat_id} not found')

    db.session.delete(flat)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Flat with id {flat_id} has been deleted'
    })
