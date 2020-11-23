from flask import Blueprint

pictures_bp = Blueprint('pictures', __name__)

from myrent_app.pictures import pictures