from flask import jsonify, abort
from webargs.flaskparser import use_args
from myrent_app import db
from myrent_app.settlements import settlements_bp
from myrent_app.models import Settlement, SettlementSchema, settlement_schema, \
                            Agreement, Flat, Landlord
from myrent_app.utils import validate_json_content_type, token_landlord_required, \
                            token_landlord_tenant_required


@settlements_bp.route('/settlements', methods=['GET'])
@token_landlord_tenant_required
def get_all_settlements(id_model_tuple: tuple):
    if id_model_tuple[1] == 'landlords':
        items = Settlement.query \
                        .join(Agreement) \
                        .join(Flat) \
                        .filter(Flat.landlord_id == id_model_tuple[0])

    if id_model_tuple[1] == 'tenants':
        items = Settlement.query \
                        .join(Agreement) \
                        .filter(Agreement.tenant_id == id_model_tuple[0])

    settlements = SettlementSchema(many=True).dump(items)

    return jsonify({
        'success': True,
        'data': settlements,
        'number_of_records': len(settlements)
    })


@settlements_bp.route('/agreements/<int:agreement_id>/settlements', 
                      methods=['GET'])
@token_landlord_tenant_required                      
def get_agreement_settlements(id_model_tuple: tuple, agreement_id: int):
    agreement = Agreement.query.get_or_404(agreement_id,
                                description=f'Agreement {agreement_id} not found')

    if id_model_tuple[1] == 'landlords':
        if agreement.flat.landlord_id != id_model_tuple[0]:
            abort(404, description=f'Agreement {agreement_id} not found')

    if id_model_tuple[1] == 'tenants':
        if agreement.tenant_id != id_model_tuple[0]:
            abort(404, description=f'Agreement {agreement_id} not found')

    settlements = SettlementSchema(many=True).dump(agreement.settlements)

    return jsonify({
        'success': True,
        'data': settlements,
        'number_of_records': len(settlements)
    })


@settlements_bp.route('/settlements/<int:settlement_id>', 
                      methods=['GET'])
@token_landlord_tenant_required                       
def get_settlement(id_model_tuple: tuple, settlement_id: int):
    settlement = Settlement.query.get_or_404(settlement_id,
                            description=f'Settlement {settlement_id} not found')

    if id_model_tuple[1] == 'landlords':
        if settlement.agreement.flat.landlord_id != id_model_tuple[0]:
            abort(404, description=f'Settlement {settlement_id} not found')

    if id_model_tuple[1] == 'tenants':
        if settlement.agreement.tenant_id != id_model_tuple[0]:
            abort(404, description=f'Settlement {settlement_id} not found')

    return jsonify({
        'success': True,
        'data': settlement_schema.dump(settlement)
    })


@settlements_bp.route('/agreements/<int:agreement_id>/settlements', 
                      methods=['POST'])
@token_landlord_required
@validate_json_content_type
@use_args(SettlementSchema(exclude=['agreement_id']), error_status_code=400)
def create_settlement(landlord_id: int, args: dict, agreement_id: int):
    agreement = Agreement.query.get_or_404(agreement_id,
                                description=f'Agreement {agreement_id} not found')
    
    if agreement.flat.landlord_id != landlord_id:
        abort(404, description=f'Agreement {agreement_id} not found')

    settlement = Settlement(agreement_id=agreement_id, **args)

    db.session.add(settlement)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': settlement_schema.dump(settlement)
    }), 201


@settlements_bp.route('/settlements/<int:settlement_id>', methods=['PUT'])
@token_landlord_required
@validate_json_content_type
@use_args(SettlementSchema(exclude=['agreement_id']), error_status_code=400)
def update_settlement(landlord_id: int, args: dict, settlement_id: int):
    settlement = Settlement.query.get_or_404(settlement_id,
                            description=f'Settlement {settlement_id} not found')

    if settlement.agreement.flat.landlord_id != landlord_id:
        abort(404, description=f'Settlement {settlement_id} not found')

    settlement.type = args['type']
    settlement.value = args['value']
    settlement.date = args['date']
    
    description = args.get('description')
    if description is not None:
        settlement.description = description

    db.session.commit()

    return jsonify({
        'success': True,
        'data': settlement_schema.dump(settlement)
    })


@settlements_bp.route('/settlements/<int:settlement_id>', methods=['DELETE'])
@token_landlord_required
def delete_settlement(landlord_id: int, settlement_id: int):
    settlement = Settlement.query.get_or_404(settlement_id,
                            description=f'Settlement {settlement_id} not found')

    if settlement.agreement.flat.landlord_id != landlord_id:
        abort(404, description=f'Settlement {settlement_id} not found')

    db.session.delete(settlement)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Settlement with id {settlement_id} has been deleted'
    })


@settlements_bp.route('/agreements/<int:agreement_id>/settlements', 
                      methods=['DELETE'])
@token_landlord_required
def delete_agreement_settlements(landlord_id: int, agreement_id: int):
    agreement = Agreement.query.get_or_404(agreement_id,
                                description=f'Agreement {agreement_id} not found')
    
    if agreement.flat.landlord_id != landlord_id:
        abort(404, description=f'Agreement {agreement_id} not found')

    for settlement in agreement.settlements:
        db.session.delete(settlement)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Settlements for agreement with id {agreement_id} has been deleted'
    })
