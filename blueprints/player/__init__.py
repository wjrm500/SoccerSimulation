from flask import Blueprint

player_bp = Blueprint("player", __name__)

from . import routes  # noqa: F401
