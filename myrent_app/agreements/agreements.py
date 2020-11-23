from flask import jsonify, abort
from webargs.flaskparser import use_args

from myrent_app import db
from myrent_app.agreements import agreements_bp
from myrent_app.models import Agreement, AgreementSchema, agreement_schema, \
                            Flat, Tenant, Landlord
from myrent_app.utils import token_landlord_tenant_required, token_landlord_required, \
                        validate_json_content_type


@agreements_bp.route('/agreements', methods=['GET'])
@token_landlord_tenant_required
def get_agreements(id_model_tuple: tuple):
    if id_model_tuple[1] == 'landlords':
        items = Agreement.query \
                        .join(Flat) \
                        .join(Landlord) \
                        .filter(Landlord.id == id_model_tuple[0])
        
    if id_model_tuple[1] == 'tenants':
        items = Agreement.query.filter_by(tenant_id=id_model_tuple[0])

    agreements = AgreementSchema(many=True).dump(items)

    return jsonify({
        'success': True,
        'data': agreements,
        'number_of_records': len(agreements)
    })


@agreements_bp.route('/agreements/<int:agreement_id>', methods=['GET'])
@token_landlord_tenant_required
def get_agreement(id_model_tuple: tuple, agreement_id: int):
    agreement = Agreement.query.get_or_404(agreement_id, 
                    description=f'Agreement with id {agreement_id} not found')

    if id_model_tuple[1] == 'landlords' and agreement.flat.landlord_id != id_model_tuple[0]:
        abort(404, description=f'Agreement with id {agreement_id} not found')

    if id_model_tuple[1] == 'tenants' and agreement.tenant_id != id_model_tuple[0]:
        abort(404, description=f'Agreement with id {agreement_id} not found')

    return jsonify({
        'success': True,
        'data': agreement_schema.dump(agreement)
    })


@agreements_bp.route('/flats/<int:flat_id>/tenants/<int:tenant_id>/agreements', 
                      methods=['POST'])
@token_landlord_required
@validate_json_content_type
@use_args(AgreementSchema(exclude=['flat_id', 'tenant_id']), error_status_code=400)
def create_agreement(landlord_id: int, args: dict, flat_id: int, tenant_id: int):

    flat = Flat.query.get_or_404(flat_id, 
                        description=f'Flat with id {flat_id} not found')
    if flat.landlord_id != landlord_id:
        abort(404, description=f'Flat with id {flat_id} not found')

    tenant = Tenant.query.get_or_404(tenant_id, 
                            description=f'Tenant with id {tenant_id} not found')
    if tenant.landlord_id != landlord_id:
        abort(404, description=f'Tenant with id {tenant_id} not found')

    agreement_with_identifier = Agreement.query.filter(
                                        Agreement.identifier == args['identifier']
                                        ).first()                   
    if agreement_with_identifier is not None:
        abort(409, description=f'Agreement with identifier {args["identifier"]} already exists')             

    agreement = Agreement(flat_id=flat_id, tenant_id=tenant_id, **args)

    db.session.add(agreement)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': agreement_schema.dump(agreement)
    }), 201


@agreements_bp.route('/agreements/<int:agreement_id>', methods=['PUT'])
@token_landlord_required
@validate_json_content_type
@use_args(AgreementSchema(exclude=['flat_id', 'tenant_id']), error_status_code=400)
def update_agreement(landlord_id: int, args: dict, agreement_id: int):
    agreement = Agreement.query.get_or_404(agreement_id, 
                    description=f'Agreement with id {agreement_id} not found')

    if agreement.flat.landlord_id != landlord_id:
        abort(404, description=f'Agreement with id {agreement_id} not found')

    agreement_with_this_identifier = Agreement.query.filter(
                                                        Agreement.identifier == args['identifier']
                                                    ).first()
    if agreement_with_this_identifier is not None and \
        agreement_with_this_identifier.identifier != args['identifier']:
        abort(409, description=f'Agreement with identifier {args["identifier"]} already exists')

    agreement.identifier = args['identifier']
    agreement.sign_date = args['sign_date']
    agreement.date_from = args['date_from']
    agreement.date_to = args['date_to']
    agreement.price_value = args['price_value']
    agreement.price_period = args['price_period']
    agreement.payment_deadline = args['payment_deadline']

    deposit_value = args.get('deposit_value')
    if deposit_value is not None:
        agreement.deposit_value = deposit_value

    description = args.get('description')
    if description is not None:
        agreement.description = description

    db.session.commit()

    return jsonify({
        'success': True,
        'data': agreement_schema.dump(agreement)
    })


@agreements_bp.route('/agreements/<int:agreement_id>', methods=['DELETE'])
@token_landlord_required
def delete_agreement(landlord_id: int, agreement_id: int):
    agreement = Agreement.query.get_or_404(agreement_id, 
                    description=f'Agreement with id {agreement_id} not found')

    if agreement.flat.landlord_id != landlord_id:
        abort(404, description=f'Agreement with id {agreement_id} not found')

    db.session.delete(agreement)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Agreement with id {agreement_id} has been deleted'
    })
