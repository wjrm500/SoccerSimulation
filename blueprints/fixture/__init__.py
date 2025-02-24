from flask import Blueprint

fixture_bp = Blueprint("fixture", __name__)

from . import routes  # noqa: E402, F401
