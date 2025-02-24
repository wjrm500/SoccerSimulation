import json

from flask import redirect, render_template, request, session, url_for
from rq import Queue

from ss.simulate import simulate
from ss.utils import make_universe_key
from utils.dependencies import TTL_SECONDS, db, r
from utils.helpers import show_simulation
from worker import conn

from . import home_bp


@home_bp.route("/", methods=["GET"])
def get_home():
    return render_template(
        "desktop/home-initial.html", css_files=["home.css"], js_files=["home.js"]
    )


@home_bp.route("/", methods=["POST"])
def post_home():
    universe_key = request.form["universe_key"]
    url = url_for("simulation.simulation", universe_key=universe_key)
    return redirect(url)


@home_bp.route("/new-simulation", methods=["GET"])
def get_new_simulation():
    systems = db.cnx["soccersim"]["systems"].find().sort("system_name", 1)
    return render_template(
        "desktop/home-new.html",
        css_files=["home.css"],
        js_files=["home.js"],
        systems=systems,
    )


@home_bp.route("/new-simulation", methods=["POST"])
def post_new_simulation():
    q = Queue(connection=conn)
    system_id = int(request.form["system"])
    custom_config = {
        "num_leagues_per_system": None,
        "num_clubs_per_league": int(request.form["num-clubs"]),
        "num_players_per_club": int(request.form["num-players-per-club"]),
        "custom_clubs": json.loads(request.form["custom-clubs"]),
    }
    universe_key = make_universe_key()
    r.set("simulation_progress_" + universe_key, 0)
    q.enqueue(simulate, custom_config, system_id, universe_key, job_timeout=3600)
    return render_template(
        "desktop/waiting.html",
        universe_key=universe_key,
        css_files=["home.css"],
        js_files=["waiting.js"],
    )


@home_bp.route("/existing-simulation", methods=["GET"])
def get_existing_simulation():
    return render_template(
        "desktop/home-existing.html", css_files=["home.css"], js_files=["home.js"]
    )


@home_bp.route("/existing-simulation", methods=["POST"])
def post_existing_simulation():
    error = "ERROR: "
    existing_how = request.form.get("existing-how")
    if existing_how == "remote":
        universe_key = request.form.get("universe-key")
        if db.universe_key_exists(universe_key):
            url = url_for("simulation.simulation", universe_key=universe_key)
            return redirect(url)
        error += f"Universe Key {universe_key} does not exist"
    elif existing_how == "local":
        file = request.files.get("upload-file")
        universe = file.read()
        new_key = make_universe_key(9)
        session["active_universe_key"] = new_key
        r.setex("simulation_" + new_key, TTL_SECONDS, universe)
        try:
            return show_simulation()
        except Exception as e:
            error += "Invalid file upload: " + str(e)
    return render_template(
        "desktop/home-existing.html",
        css_files=["home.css"],
        js_files=["home.js"],
        error=error,
    )
