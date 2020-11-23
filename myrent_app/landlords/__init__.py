from flask import Blueprint

landlords_bp = Blueprint('landlords', __name__)

from myrent_app.landlords import landlords
