from flask import Blueprint

simulation_bp = Blueprint("simulation", __name__)

from . import routes  # noqa: E402, F401
