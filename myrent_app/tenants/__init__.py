from flask import Blueprint

tenants_bp = Blueprint('tenants', __name__)

from myrent_app.tenants import tenants
