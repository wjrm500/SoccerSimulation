from flask import Blueprint

general_bp = Blueprint("general", __name__)

from . import routes  # noqa: E402, F401
