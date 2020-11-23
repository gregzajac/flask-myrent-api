from flask import Blueprint

flats_bp = Blueprint('flats', __name__)

from myrent_app.flats import flats