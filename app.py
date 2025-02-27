import os

from flask import Flask
from flask_mobility import Mobility
from flask_session import Session

import ss.utils as utils


def create_app():
    """Application factory function"""
    # Configure app
    template_folder = os.path.abspath("frontend/templates")
    static_folder = os.path.abspath("frontend/static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
    app.config["SESSION_TYPE"] = "filesystem"

    # Initialise extensions
    Session(app)
    Mobility(app)

    # Register blueprints
    from blueprints.club import club_bp
    from blueprints.fixture import fixture_bp
    from blueprints.general import general_bp
    from blueprints.home import home_bp
    from blueprints.player import player_bp
    from blueprints.simulation import simulation_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(club_bp)
    app.register_blueprint(fixture_bp)
    app.register_blueprint(general_bp)

    @app.context_processor
    def inject_dict_for_all_templates():
        random_string = utils.generate_random_digits(5)
        return {"random_string": random_string}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
