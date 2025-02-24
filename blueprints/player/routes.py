import io
from datetime import timedelta

import matplotlib.pyplot as plt
from flask import Response, render_template, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import ss.player_utils as player_utils
from utils.helpers import get_search_gameweek, get_universe

from . import player_bp


@player_bp.route("/simulation/player/<id>")
def player(id):
    universe = get_universe()
    search_gameweek = get_search_gameweek(universe.systems[0].leagues[0])
    player = universe.player_controller.get_player_by_id(id)
    performance_indices = player.club.league.get_performance_indices(
        sort_by="performance_index", gameweek=search_gameweek
    )[player]
    max_date = None
    if request.args.get("gameweek"):
        max_date = player.club.league.gameweek_dates[search_gameweek]
    injuries = []
    for injury in player.injuries:
        start_date = injury[0]
        if max_date is not None and start_date > max_date:
            continue
        injury_length = injury[1]
        end_date = start_date + timedelta(int(injury_length))
        if max_date is not None and end_date > max_date:
            injury_text = "Since {}".format(start_date.strftime("%d %b"))
        else:
            injury_text = "Between {} and {} ({} days)".format(
                start_date.strftime("%d %b"), end_date.strftime("%d %b"), injury_length
            )
        injuries.append(injury_text)
    performance_indices["injuries"] = injuries
    yR = [val["rating"] for val in list(player.ratings.values())]
    yPR = [val["peak_rating"] for val in list(player.ratings.values())]
    player_development = {
        "rating": {
            "start": yR[0],
            "end": player.ratings[max_date]["rating"] if request.args.get("gameweek") else yR[-1],
        },
        "peak_rating": {
            "start": yPR[0],
            "end": player.ratings[max_date]["peak_rating"]
            if request.args.get("gameweek")
            else player.peak_rating,
        },
    }
    player_best_position = (
        player.get_best_position(player.get_skill_distribution(player.get_age_on_date(max_date)))
        if request.args.get("gameweek")
        else player.get_best_position()
    )
    return render_template(
        "desktop/player/player.html",
        css_files=["rest_of_website.css", "iframe.css"],
        js_files=["iframe.js", "player.js"],
        player=player,
        player_best_position=player_best_position,
        player_rating=player.ratings[max_date]["rating"]
        if request.args.get("gameweek")
        else player.get_rating(),
        player_peak_rating=player.ratings[max_date]["peak_rating"]
        if request.args.get("gameweek")
        else player.peak_rating,
        player_age=player.get_age_on_date(max_date, 2)
        if request.args.get("gameweek")
        else player.get_age(2),
        player_reports=player.get_player_reports(search_gameweek),
        performance_indices=performance_indices,
        player_development=player_development,
    )


@player_bp.route("/simulation/player/<player_id>/radar")
def player_radar(player_id):
    universe = get_universe()
    player = universe.player_controller.get_player_by_id(player_id)
    league = universe.systems[0].leagues[0]
    search_gameweek = get_search_gameweek(league)
    if request.args.get("gameweek"):
        max_date = league.gameweek_dates[search_gameweek]
    else:
        max_date = None
    date = max_date if request.args.get("gameweek") else None
    fig = player_utils.show_skill_distribution(player, date=date, projection=True)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")


@player_bp.route("/simulation/player/<player_id>/form-graph")
def player_form_graph(player_id):
    universe = get_universe()
    player = universe.player_controller.get_player_by_id(player_id)
    fig = player_utils.show_player_form(player)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")


@player_bp.route("/simulation/player/<player_id>/development-graph")
def player_development_graph(player_id):
    universe = get_universe()
    league = universe.systems[0].leagues[0]
    date = None
    if request.args.get("gameweek"):
        search_gameweek = get_search_gameweek(league)
        max_date = league.gameweek_dates[search_gameweek]
        date = max_date
    player = universe.player_controller.get_player_by_id(player_id)
    fig = player_utils.show_player_development(player, date=date)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")
