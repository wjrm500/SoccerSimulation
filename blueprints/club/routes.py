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

    # Get match reports filtered by club and gameweek
    match_reports = [
        report
        for report in club.league.match_reports
        if (club == report.home_club or club == report.away_club)
        and (search_gameweek is None or report.gameweek <= search_gameweek)
    ]

    results = []
    for match_report in match_reports:
        at_home = club == match_report.home_club
        opp_club = match_report.away_club if at_home else match_report.home_club
        club_report = match_report.clubs_reports[club]
        opp_club_report = match_report.clubs_reports[opp_club]

        result = {
            "at_home": at_home,
            "fixture_id": match_report.fixture_id,
            "gameweek": match_report.gameweek,
            "club": club,
            "opp_club": opp_club,
            "club_score": club_report.goals_for,
            "opp_club_score": opp_club_report.goals_for,
            "result": club_report.outcome,
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
