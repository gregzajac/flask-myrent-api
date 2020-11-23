import re
import jwt
from flask import request, abort, current_app, url_for
from flask_sqlalchemy import DefaultMeta, BaseQuery
from functools import wraps
from typing import Tuple
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from werkzeug.exceptions import UnsupportedMediaType
from werkzeug.security import generate_password_hash


COMPARISON_OPERATORS_RE = re.compile(r'(.*)\[(gte|lte|gt|lt)\]')

def validate_json_content_type(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None:
            raise UnsupportedMediaType('Content type must be application/json')
        return func(*args, **kwargs)
    return wrapper

def token_landlord_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization')

        if auth:
            token = auth.split(' ')[1]
        if token is None:
            abort(401, description='Missing landlord token. Please login or register as landlord.')

        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), 
                                algorithms=['HS256'])

            if payload['model'] != 'landlords':
                abort(401, description='Only landlord functionality')
        except jwt.ExpiredSignatureError:
            abort(401, description='Expired token. Please login as landlord to get new token.')
        except jwt.InvalidTokenError:
            abort(401, description='Invalid token. Please login or register as landlord.')
        return func(payload['id'], *args, **kwargs)
    return wrapper

def token_landlord_tenant_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization')
        
        if auth:
            token = auth.split(' ')[1]
        if token is None:
            abort(401, description='Missing token. Please login or register.')
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        
        return func((payload['id'], payload['model']), *args, **kwargs)
    return wrapper

def get_schema_args(model: DefaultMeta) -> dict:
    fields = request.args.get('fields')
    schema_args = {'many': True}
    if fields:
        schema_args['only'] = [field for field in fields.split(',') if field in model.__table__.columns]
    return schema_args

def apply_order(model: DefaultMeta, query: BaseQuery) -> BaseQuery: 
    """
    Functionality of sorting resources, returns sort arguments to query
    (example: sort=-id,last_name).
    """        
    sort_keys = request.args.get('sort')        
    if sort_keys:
        for key in sort_keys.split(','):
            desc = False
            if key.startswith('-'):
                key = key[1:]
                desc = True
            column_attr = getattr(model, key, None)
            if column_attr is not None:
                query = query.order_by(column_attr.desc()) if desc else query.order_by(column_attr)   
    return query

def _get_filter_argument(column_name: InstrumentedAttribute, 
                        value: str, 
                        operator: str) -> BinaryExpression:
    operator_mapping = {
        '==': column_name == value,
        'gte': column_name >= value,
        'gt': column_name > value,
        'lte': column_name <= value,
        'lt': column_name < value,
    }
    return operator_mapping[operator]

def apply_filter(model: DefaultMeta, query: BaseQuery) -> BaseQuery:
    """
    Functionality of filtering resources, returns filter arguments to query
    (example: id[gte]=3)
    """
    params = request.args.items()
    if params:
        for param, value in params:
            if param not in ['fields', 'sort', 'page', 'limit']:
                operator = '=='
                match = COMPARISON_OPERATORS_RE.match(param)
                if match is not None:
                    param, operator = match.groups()
                column_attr = getattr(model, param, None)
                if column_attr is not None:
                    value = model.additional_validation(param, value)
                    if value is None:
                        continue
                    filter_argument = _get_filter_argument(column_attr, value, operator)
                    query = query.filter(filter_argument)
    return query


def get_pagination(query: BaseQuery, func_name: str) -> Tuple[list, dict]:
    """
    Functionality of paginating response, returns modified query
    page - page number to return
    limit - number of items in one page to return
    """        
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', current_app.config.get('PER_PAGE', 5), type=int)
    params = {key: value for key, value in request.args.items() if key != 'page'}
    paginate_obj = query.paginate(page, limit, False)

    pagination = {
        'total_pages': paginate_obj.pages,
        'total_records': paginate_obj.total,
        'current_page': url_for(func_name, page=page, **params)
    }

    if paginate_obj.has_next:
        pagination['next_page'] = url_for(func_name, page=page+1, **params)
    if paginate_obj.has_prev:
        pagination['previous_page'] = url_for(func_name, page=page-1, **params)
    
    return paginate_obj.items, pagination


def generate_hashed_password(password: str) -> str:
    return generate_password_hash(password)


def allowed_picture(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS')    
