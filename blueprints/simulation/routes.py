import json

from flask import jsonify, render_template, request, session

from ss.config import player_config
from utils.dependencies import TTL_SECONDS, db, r
from utils.helpers import get_search_gameweek, get_universe, show_simulation

from . import simulation_bp


@simulation_bp.route("/simulation/<universe_key>")
def simulation(universe_key):
    session["active_universe_key"] = universe_key
    universe_data = db.get_universe_grid_file(universe_key)
    if universe_data is None:
        return "Universe not found", 404
    return show_simulation()


@simulation_bp.route("/simulation/check-progress/<universe_key>", methods=["GET"])
def check_simulation_progress(universe_key):
    redis_key = "simulation_progress_" + universe_key
    if r.exists(redis_key):
        return r.get(redis_key).decode("utf-8")


@simulation_bp.route(
    "/simulation/check-universe-key-exists-in-database/<universe_key>", methods=["GET"]
)
def check_universe_key_exists_in_database(universe_key):
    universe = db.get_universe_grid_file(universe_key)
    if universe:
        session["active_universe_key"] = universe_key
        r.setex("simulation_" + universe_key, TTL_SECONDS, universe)
        return json.dumps(True)
    return json.dumps(False)


@simulation_bp.route("/simulation/store-email", methods=["POST"])
def store_email():
    email_input = request.form.get("email_input")
    universe_key = request.form.get("universe_key")
    r.set("email_" + universe_key, email_input)
    return jsonify("success")


@simulation_bp.route("/simulation/default-iframe")
def default():
    return render_template("desktop/default_iframe.html", css_files=["rest_of_website.css"])


@simulation_bp.route("/simulation/player-performance")
def player_performance():
    universe = get_universe()
    league = universe.systems[0].leagues[0]
    search_gameweek = get_search_gameweek(league)
    player_performance_items = league.get_performance_indices(
        sort_by="performance_index", gameweek=search_gameweek
    )
    filter_clubs = sorted(
        [{"id": club.id, "name": club.name} for club in league.clubs],
        key=lambda x: x["name"],
    )
    filter_positions = list(player_config["positions"].keys())
    return render_template(
        "desktop/player_performance_proper.html",
        css_files=["rest_of_website.css", "iframe.css"],
        js_files=["iframe.js", "player_performance.js"],
        filter_clubs=filter_clubs,
        filter_positions=filter_positions,
        player_performance_items=player_performance_items,
    )
