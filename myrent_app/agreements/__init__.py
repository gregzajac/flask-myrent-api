from flask import Blueprint

agreements_bp = Blueprint('agreements', __name__)

from myrent_app.agreements import agreements