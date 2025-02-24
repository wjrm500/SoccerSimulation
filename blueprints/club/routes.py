import io
import json

import matplotlib.pyplot as plt
from flask import Response, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import ss.club_utils as club_utils
from utils.helpers import get_search_gameweek, get_universe

from . import club_bp


@club_bp.route("/simulation/club/<club_id>")
def club(club_id):
    universe = get_universe()
    club = universe.get_club_by_id(club_id)
    team = club.select_team(test=True)
    selection = team.selection
    formation = team.formation
    average_select_rating = sum([select.rating for select in selection]) / 10
    players = json.dumps(
        [
            {
                "adjusted_rating": (select.rating - average_select_rating) / average_select_rating,
                "id": select.player.id,
                "name": select.player.get_club_specific_name(),
                "position": select.position,
                "rating": select.rating,
            }
            for select in selection
        ]
    )
    search_gameweek = get_search_gameweek(universe.systems[0].leagues[0])
    player_performance_items = club.league.get_performance_indices(
        sort_by="performance_index", gameweek=search_gameweek, clubs=club
    )

    results = []
    for match_report in club.get_match_reports(search_gameweek):
        at_home = club == list(match_report["clubs"].keys())[0]
        opp_club = [x for x in list(match_report["clubs"].keys()) if x != club][0]
        club_score = match_report["clubs"][club]["match"]["goals_for"]
        opp_club_score = match_report["clubs"][opp_club]["match"]["goals_for"]
        result = {
            "at_home": at_home,
            "fixture_id": match_report["fixture_id"],
            "gameweek": match_report["gameweek"],
            "club": club,
            "opp_club": opp_club,
            "club_score": club_score,
            "opp_club_score": opp_club_score,
            "result": "win"
            if club_score > opp_club_score
            else "loss"
            if opp_club_score > club_score
            else "draw",
        }
        results.append(result)
    return render_template(
        "desktop/club/club.html",
        css_files=["rest_of_website.css", "iframe.css"],
        js_files=["club.js", "iframe.js"],
        club=club,
        formation=formation,
        players=players,
        player_performance_items=player_performance_items,
        results=results,
    )


@club_bp.route("/simulation/club/<club_id>/position-graph")
def club_position_graph(club_id):
    universe = get_universe()
    club = universe.get_club_by_id(club_id)
    search_gameweek = get_search_gameweek(universe.systems[0].leagues[0])
    fig = club_utils.show_club_positions(club, gameweek=search_gameweek)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")
