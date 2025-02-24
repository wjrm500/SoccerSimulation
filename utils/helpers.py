# utils/helpers.py
import pickle

from flask import abort, g, render_template, request, session

from utils.dependencies import db


def get_universe():
    """Get the universe object from session or GridFS"""
    if "universe" not in g:
        active_key = session.get("active_universe_key")
        if not active_key:
            abort(400, description="Simulation not set")
        universe_data = db.get_universe_grid_file(active_key)
        if universe_data is None:
            abort(404, description="Simulation data not found")
        g.universe = pickle.loads(universe_data)
    return g.universe


def get_search_gameweek(league):
    """Get the gameweek to use based on query params or default to max"""
    gameweek = request.args.get("gameweek") or ""
    last_gameweek = (len(league.clubs) - 1) * 2
    search_gameweek = last_gameweek
    if gameweek.isnumeric():
        gameweek = int(gameweek)
        if gameweek <= last_gameweek:
            search_gameweek = gameweek
    return search_gameweek


def show_simulation():
    """Generate simulation view data and render template"""
    active_universe_key = session["active_universe_key"]
    universe = get_universe()
    league = universe.systems[0].leagues[0]

    search_gameweek = get_search_gameweek(league)

    # Get standings
    league_table = league.get_league_table(search_gameweek)
    league_table_items = list(league_table.items())
    league_table_items.sort(key=lambda x: (x[1]["Pts"], x[1]["GD"]), reverse=True)

    # Get player performance
    player_performance_items = league.get_performance_indices(
        sort_by="performance_index", gameweek=search_gameweek
    )

    # Get results
    dates = {}
    for match_report in league.match_reports:
        if match_report["gameweek"] > search_gameweek:
            break
        clubs = list(match_report["clubs"].keys())
        if len(clubs) >= 2:
            club_a, club_b = clubs[0], clubs[1]
        else:
            club_a = clubs[0]
            club_b = None
        match = list(match_report["clubs"].values())[0]["match"]
        score_a, score_b = match["goals_for"], match["goals_against"]
        result = {
            "fixture_id": match_report["fixture_id"],
            "home_club": club_a,
            "away_club": club_b,
            "home_score": score_a,
            "away_score": score_b,
        }
        if match_report["date"] not in dates:
            dates[match_report["date"]] = []
        dates[match_report["date"]].append(result)

    if request.MOBILE:
        return render_template(
            "mobile/simulation.html",
            css_files=["rest_of_website.css", "mobile.css"],
            js_files=["mobile.js"],
            universe_key=active_universe_key,
            league_table_items=league_table_items,
            player_performance_items=player_performance_items,
            dates=dates,
        )

    return render_template(
        "desktop/simulation.html",
        css_files=["rest_of_website.css"],
        js_files=["script.js"],
        universe_key=active_universe_key,
        league_table_items=league_table_items,
        player_performance_items=player_performance_items,
        dates=dates,
    )
