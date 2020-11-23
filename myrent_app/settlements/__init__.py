from flask import Blueprint

settlements_bp = Blueprint('settlements', __name__)

from myrent_app.settlements import settlements
