import os
from io import BytesIO

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_mobility import Mobility
from flask_session import Session

import ss.utils as utils
from blueprints.club import club_bp
from blueprints.fixture import fixture_bp
from blueprints.home import home_bp
from blueprints.player import player_bp
from blueprints.simulation import simulation_bp
from utils.dependencies import db

template_folder = os.path.abspath("frontend/templates")
static_folder = os.path.abspath("frontend/static")
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.register_blueprint(club_bp)
app.register_blueprint(fixture_bp)
app.register_blueprint(home_bp)
app.register_blueprint(player_bp)
app.register_blueprint(simulation_bp)
app.secret_key = os.urandom(12).hex()
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
Mobility(app)


@app.route("/download/<universe_key>")
def download(universe_key):
    universe_data = db.get_universe_grid_file(universe_key)
    if universe_data is None:
        return "Simulation data not found", 404
    attachment_filename = "universe_" + universe_key
    return send_file(BytesIO(universe_data), download_name=attachment_filename, as_attachment=True)


@app.route("/about", methods=["GET"])
def about():
    if request.MOBILE:
        return render_template("mobile/about.html", css_files=["rest_of_website.css", "mobile.css"])
    return render_template(
        "desktop/about.html", css_files=["rest_of_website.css"], js_files=["script.js"]
    )


@app.route("/contact", methods=["GET"])
def contact():
    if request.MOBILE:
        return render_template(
            "mobile/contact.html", css_files=["rest_of_website.css", "mobile.css"]
        )
    return render_template(
        "desktop/contact.html", css_files=["rest_of_website.css"], js_files=["script.js"]
    )


@app.context_processor
def inject_dict_for_all_templates():
    random_string = utils.generate_random_digits(5)
    return {"random_string": random_string}


### Dev methods for convenience
@app.route("/clear", methods=["GET"])
def clear_session():
    session.clear()
    url = url_for("get_home")
    return redirect(url)
