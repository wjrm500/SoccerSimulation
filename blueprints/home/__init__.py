from flask import Blueprint

home_bp = Blueprint("home", __name__)

from . import routes  # noqa: E402, F401
