import jwt
from flask import current_app
from datetime import datetime, timedelta
from marshmallow import Schema, fields, validate
from werkzeug.security import check_password_hash
from myrent_app import db


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Landlord(TimestampMixin, db.Model):
    __tablename__ = 'landlords'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)
    flats = db.relationship('Flat', back_populates='landlord')
    tenants = db.relationship('Tenant', back_populates='landlord')


    def __repr__(self):
        return f'<landlord>: {self.first_name} {self.last_name}'

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value         

    def generate_jwt(self) -> bytes:
        jwt_expired_minutes = current_app.config.get('JWT_EXPIRED_MINUTES', 30)
        payload = {
            'id': self.id,
            'model': 'landlords',
            'exp': datetime.utcnow() + timedelta(minutes=jwt_expired_minutes)
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY'))

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Flat(TimestampMixin, db.Model):
    __tablename__ = 'flats'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  #active/inactive/sold
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'), nullable=False)
    landlord = db.relationship('Landlord', back_populates='flats')
    agreements = db.relationship('Agreement', back_populates='flat')
    pictures = db.relationship('Picture', back_populates='flat')

    def __repr__(self):
        return f'<flat>: {self.id} {self.identifier}'

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value         


class Picture(TimestampMixin, db.Model):
    __tablename__ = 'pictures'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable = False)
    path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    flat_id = db.Column(db.Integer, db.ForeignKey('flats.id'), nullable=False)
    flat = db.relationship('Flat', back_populates='pictures')

    def __repr__(self):
        return f'<picture>: {self.id} - {self.name}'

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value         


class Tenant(TimestampMixin, db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'), nullable=False)
    landlord = db.relationship('Landlord', back_populates='tenants')
    agreements = db.relationship('Agreement', back_populates='tenant')

    def __repr__(self):
        return f'<tenant>: {self.first_name} {self.last_name}'

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value         

    def generate_jwt(self) -> bytes:
        jwt_expired_minutes = current_app.config.get('JWT_EXPIRED_MINUTES', 30)
        payload = {
            'id': self.id,
            'model': 'tenants',
            'exp': datetime.utcnow() + timedelta(minutes=jwt_expired_minutes)
        }

        return jwt.encode(payload, current_app.config.get('SECRET_KEY'))

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Agreement(TimestampMixin, db.Model):
    __tablename__ = 'agreements'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sign_date = db.Column(db.Date, nullable=False)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    price_value = db.Column(db.Float, nullable=False)
    price_period = db.Column(db.String(10), nullable=False)  #'day'/'month'
    payment_deadline = db.Column(db.Integer, nullable=False)
    deposit_value = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    flat_id = db.Column(db.Integer, db.ForeignKey('flats.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    flat = db.relationship('Flat', back_populates='agreements')
    tenant = db.relationship('Tenant', back_populates='agreements')
    settlements = db.relationship('Settlement', back_populates='agreement')

    def __repr__(self):
        return f'<agreement>: {self.identifier} - {self.flat} - {self.tenant}'

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        if param in ['sign_date', 'date_from', 'date_to']:
            try:
                value = datetime.strptime(value, '%d-%m-%Y').date()
            except ValueError:
                value = None
        return value


class Settlement(TimestampMixin, db.Model):
    __tablename__ = 'settlements'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    description = db.Column(db.Text)
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id'), nullable=False)
    agreement = db.relationship('Agreement', back_populates='settlements')

    def __repr__(self):
        return f'<settlement>: {self.id} {self.agreement}'

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        if param == 'date':
            try:
                value = datetime.strptime(value, '%d-%m-%Y').date()
            except ValueError:
                value = None
        return value


class LandlordSchema(Schema):
    id = fields.Integer(dump_only=True)
    identifier = fields.String(required=True, validate=validate.Length(min=3, max=255))
    email = fields.String(required=True, validate=validate.Length(max=255))
    first_name = fields.String(required=True, validate=validate.Length(max=100))
    last_name = fields.String(required=True, validate=validate.Length(max=100))
    phone = fields.String(required=True, validate=validate.Length(max=50))
    address = fields.String(required=True, validate=validate.Length(max=255))
    description = fields.String()
    password = fields.String(load_only=True, required=True, 
                    validate=validate.Length(min=6, max=255))
    flats = fields.List(fields.Nested(lambda: FlatSchema(exclude=['landlord'])))
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)


class LandlordUpdatePasswordSchema(Schema):
    current_password = fields.String(required=True, load_only=True, 
                            validate=validate.Length(min=6, max=255))
    new_password = fields.String(required=True, load_only=True, 
                        validate=validate.Length(min=6, max=255))


class FlatSchema(Schema):
    id = fields.Integer(dump_only=True)
    identifier = fields.String(required=True, 
                    validate=validate.Length(min=3, max=255))
    address = fields.String(required=True, 
                    validate=validate.Length(min=3, max=255))
    description = fields.String()
    status = fields.String()
    landlord_id = fields.Integer(load_only=True)
    landlord = fields.Nested(lambda: LandlordSchema(only=['id',
                                                        'identifier', 
                                                        'first_name', 
                                                        'last_name']))
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)


class TenantSchema(Schema):
    id = fields.Integer(dump_only=True)
    identifier = fields.String(required=True, validate=validate.Length(min=3, max=255))
    email = fields.String(required=True, validate=validate.Length(max=255))
    first_name = fields.String(required=True, validate=validate.Length(max=100))
    last_name = fields.String(required=True, validate=validate.Length(max=100))
    phone = fields.String(required=True, validate=validate.Length(max=50))
    address = fields.String(required=True, validate=validate.Length(max=255))
    description = fields.String()
    password = fields.String(load_only=True, required=True, 
                    validate=validate.Length(min=6, max=255))
    landlord_id = fields.Integer(load_only=True)
    landlord = fields.Nested(lambda: LandlordSchema(only=['id',
                                                        'identifier', 
                                                        'first_name', 
                                                        'last_name']))
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)    


class TenantUpdatePasswordSchema(Schema):
    current_password = fields.String(required=True, load_only=True, 
                            validate=validate.Length(min=6, max=255))
    new_password = fields.String(required=True, load_only=True, 
                        validate=validate.Length(min=6, max=255))


class AgreementSchema(Schema):
    id = fields.Integer(dump_only=True)
    identifier = fields.String(required=True, validate=validate.Length(min=3, max=50))
    sign_date = fields.Date('%d-%m-%Y', required=True)
    date_from = fields.Date('%d-%m-%Y', required=True)
    date_to = fields.Date('%d-%m-%Y', required=True)
    price_value = fields.Float(required=True)
    price_period = fields.String(required=True, validate=validate.Length(max=10))
    payment_deadline = fields.Integer(required=True)
    deposit_value = fields.Float()
    description = fields.String()
    flat_id = fields.Integer(load_only=True)
    tenant_id = fields.Integer(load_only=True)
    flat = fields.Nested(lambda: FlatSchema(only=['id',
                                                'identifier',
                                                'address']))
    tenant = fields.Nested(lambda: TenantSchema(only=['id',
                                                    'identifier',
                                                    'first_name',
                                                    'last_name']))
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True) 


class SettlementSchema(Schema):
    id = fields.Integer(dump_only=True)
    type = fields.String(required=True, validate=validate.OneOf(
                                                            ['charge', 
                                                            'payment']))
    value = fields.Float()
    date = fields.Date('%d-%m-%Y', required=True)
    description = fields.String()
    agreement_id = fields.Integer(load_only=True)
    agreement = fields.Nested(lambda: AgreementSchema(only=['id',
                                                        'identifier',
                                                        'sign_date']))
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True) 


class PictureSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))
    path = fields.String(required=True, validate=validate.Length(max=255))
    description = fields.String()
    flat_id = fields.Integer(load_only=True)
    flat = fields.Nested(lambda: FlatSchema(only=['id',
                                                'identifier',
                                                'address']))
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)                                                    


landlord_schema = LandlordSchema()
landlord_update_password_schema = LandlordUpdatePasswordSchema()
flat_schema = FlatSchema()
tenant_schema = TenantSchema()
tenant_update_password_schema = TenantUpdatePasswordSchema()
agreement_schema = AgreementSchema()
settlement_schema = SettlementSchema()
picture_schema = PictureSchema()
