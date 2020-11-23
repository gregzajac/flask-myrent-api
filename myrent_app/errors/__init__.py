from flask import Blueprint

errors_bp = Blueprint('errors', __name__)

from myrent_app.errors import errors