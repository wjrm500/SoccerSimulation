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
from blueprints.home import home_bp
from blueprints.player import player_bp
from blueprints.simulation import simulation_bp
from utils.dependencies import db
from utils.helpers import get_universe

template_folder = os.path.abspath("frontend/templates")
static_folder = os.path.abspath("frontend/static")
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.register_blueprint(club_bp)
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


@app.route("/simulation/fixture/<fixture_id>")
def fixture(fixture_id):
    universe = get_universe()
    fixture = universe.get_fixture_by_id(int(fixture_id))
    club_data = []
    for club, data in fixture.match.match_report["clubs"].items():
        club_datum = data
        club_datum["id"] = club.id
        club_datum["name"] = club.name
        club_data.append(club_datum)
    home_club_data, away_club_data = club_data

    def get_reverse_fixture(fixture):
        for other_fixture in fixture.tournament.fixtures:
            if fixture.club_x == other_fixture.club_y and fixture.club_y == other_fixture.club_x:
                return other_fixture

    positions = ["CF", "WF", "COM", "WM", "CM", "CDM", "WB", "FB", "CB"]
    for club_data in [home_club_data, away_club_data]:
        reordered_players = sorted(
            club_data["players"].items(), key=lambda x: positions.index(x[1]["position"])
        )
        club_data["players"] = dict(reordered_players)
        for player, data in club_data["players"].items():
            pre_match_form = data["pre_match_form"]
            prefix = "+" if pre_match_form > 0 else "±" if pre_match_form == 0 else ""
            pre_match_form_text = f"{prefix}{pre_match_form:.2f}"
            club_data["players"][player]["extra_data"]["pre_match_form"] = pre_match_form_text
            club_data["players"][player]["extra_data"]["select_rating"] = "{:.2f}".format(
                data["extra_data"]["select_rating"]
            )
            club_data["players"][player]["performance_index"] = "{:.2f}".format(
                data["performance_index"]
            )

    reverse_fixture_data = {}
    reverse_fixture = get_reverse_fixture(fixture)
    reverse_fixture_data["fixture_id"] = reverse_fixture.id
    reverse_fixture_data["homeTeam"] = reverse_fixture.club_x.name
    reverse_fixture_data["homeGoals"] = reverse_fixture.match.match_report["clubs"][
        reverse_fixture.club_x
    ]["match"]["goals_for"]
    reverse_fixture_data["awayTeam"] = reverse_fixture.club_y.name
    reverse_fixture_data["awayGoals"] = reverse_fixture.match.match_report["clubs"][
        reverse_fixture.club_y
    ]["match"]["goals_for"]

    recent_results = {}
    pre_match_league_tables = {"name": "Pre-match", "data": {}}
    post_match_league_tables = {"name": "Post-match", "data": {}}
    for club in fixture.match.match_report["clubs"]:
        recent_results[club] = {"points": 0, "results": []}
        fixtures_involving_club = list(
            filter(lambda x: club in x.clubs, fixture.tournament.fixtures)
        )
        fixture_index = fixtures_involving_club.index(fixture)
        for i, league_tables in enumerate([pre_match_league_tables, post_match_league_tables]):
            league_table = (
                fixture.tournament.get_league_table(fixture_index + i)
                if fixture_index > 0
                else None
            )
            if league_table:
                league_table_items = list(league_table.items())
                league_table_items.sort(key=lambda x: (x[1]["Pts"], x[1]["GD"]), reverse=True)
                for j, league_table_item in enumerate(league_table_items):
                    league_table_item[1]["#"] = j + 1
                    if league_table_item[0] == club:
                        table_index = j
                if table_index < 1:
                    start_table_index = 0
                    end_table_index = 3
                elif table_index > (len(league_table_items) - 2):
                    start_table_index = len(league_table_items) - 3
                    end_table_index = len(league_table_items)
                else:
                    start_table_index = table_index - 1
                    end_table_index = table_index + 2
                league_table = league_table_items[start_table_index:end_table_index]
                league_tables["data"][club] = league_table

        fixtures_of_interest = fixtures_involving_club[
            fixture_index - min(fixture_index, 6) : fixture_index
        ]
        for fixture_of_interest in fixtures_of_interest:
            result = (
                "D"
                if "winner" not in fixture_of_interest.match.match_report
                else "W"
                if fixture_of_interest.match.match_report["winner"] == club
                else "L"
            )
            recent_results[club]["points"] += 3 if result == "W" else 1 if result == "D" else 0
            score = "{} {} - {} {}".format(
                fixture_of_interest.club_x.name,
                fixture_of_interest.match.match_report["clubs"][fixture_of_interest.club_x][
                    "match"
                ]["goals_for"],
                fixture_of_interest.match.match_report["clubs"][fixture_of_interest.club_y][
                    "match"
                ]["goals_for"],
                fixture_of_interest.club_y.name,
            )
            fixture_id = fixture_of_interest.id
            recent_results[club]["results"].append(
                {"result": result, "score": score, "fixture_id": fixture_id}
            )

    return render_template(
        "desktop/fixture/fixture.html",
        css_files=["rest_of_website.css", "iframe.css"],
        js_files=["fixture.js", "iframe.js"],
        fixture=fixture,
        home_club_data=home_club_data,
        away_club_data=away_club_data,
        reverse_fixture=reverse_fixture_data,
        recent_results=recent_results,
        pre_match_league_tables=pre_match_league_tables,
        post_match_league_tables=post_match_league_tables,
        num_clubs=len(universe.systems[0].leagues[0].clubs),
    )


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
