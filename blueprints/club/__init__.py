from flask import Blueprint

club_bp = Blueprint("club", __name__)

from . import routes  # noqa: E402, F401
