from flask import render_template

from utils.helpers import get_universe

from . import fixture_bp


@fixture_bp.route("/simulation/fixture/<fixture_id>")
def fixture(fixture_id):
    universe = get_universe()
    fixture = universe.get_fixture_by_id(int(fixture_id))
    match_report = fixture.match.match_report

    # Format player performance data for display
    positions = ["CF", "WF", "COM", "WM", "CM", "CDM", "WB", "FB", "CB"]

    # Format player display data
    home_players = []
    away_players = []

    # Get player data directly from the player reports
    for club, team_report in match_report.clubs_reports.items():
        player_list = []
        for player, player_report in team_report.players.items():
            # Format some display values
            pre_match_form = player_report.pre_match_form
            prefix = "+" if pre_match_form > 0 else "±" if pre_match_form == 0 else ""
            pre_match_form_text = f"{prefix}{pre_match_form:.2f}"

            # Format a few specific values for display
            player_data = {
                "player": player,
                "report": player_report,
                "formatted_select_rating": f"{player_report.extra_data['select_rating']:.2f}",
                "formatted_performance_index": f"{player_report.performance_index:.2f}",
                "formatted_pre_match_form": pre_match_form_text,
            }
            player_list.append(player_data)

        # Sort players by position
        player_list.sort(key=lambda x: positions.index(x["report"].position))

        # Add to appropriate club's player list
        if club == fixture.club_x:
            home_players = player_list
        else:
            away_players = player_list

    # Find reverse fixture
    def get_reverse_fixture(fixture):
        for other_fixture in fixture.league.fixtures:
            if fixture.club_x == other_fixture.club_y and fixture.club_y == other_fixture.club_x:
                return other_fixture

    reverse_fixture = get_reverse_fixture(fixture)

    # Get recent results
    recent_results = {}
    pre_match_league_tables = {"name": "Pre-match", "data": {}}
    post_match_league_tables = {"name": "Post-match", "data": {}}

    for club in [fixture.club_x, fixture.club_y]:
        # Get recent results
        recent_results[club] = {"points": 0, "results": []}
        fixtures_involving_club = [f for f in fixture.league.fixtures if club in f.clubs]
        fixture_index = fixtures_involving_club.index(fixture)

        # Get league tables
        for i, league_tables in enumerate([pre_match_league_tables, post_match_league_tables]):
            league_table = (
                fixture.league.get_league_table(fixture_index + i) if fixture_index > 0 else None
            )
            if league_table:
                league_table_items = list(league_table.items())
                league_table_items.sort(key=lambda x: (x[1]["Pts"], x[1]["GD"]), reverse=True)
                table_index = None
                for j, league_table_item in enumerate(league_table_items):
                    league_table_item[1]["#"] = j + 1
                    if league_table_item[0] == club:
                        table_index = j

                # Get relevant section of table
                if table_index is not None:
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

        # Get recent fixtures
        fixtures_of_interest = fixtures_involving_club[
            fixture_index - min(fixture_index, 6) : fixture_index
        ]

        for fixture_of_interest in fixtures_of_interest:
            interest_match_report = fixture_of_interest.match.match_report
            club_report = interest_match_report.clubs_reports[club]

            result = club_report.outcome
            points = 3 if result == "win" else 1 if result == "draw" else 0
            recent_results[club]["points"] += points

            # Format score display
            home_club = fixture_of_interest.club_x
            away_club = fixture_of_interest.club_y
            home_goals = interest_match_report.clubs_reports[home_club].goals_for
            away_goals = interest_match_report.clubs_reports[away_club].goals_for

            score = f"{home_club.name} {home_goals} - {away_goals} {away_club.name}"
            result_code = "W" if result == "win" else "D" if result == "draw" else "L"

            recent_results[club]["results"].append(
                {"result": result_code, "score": score, "fixture_id": fixture_of_interest.id}
            )

    return render_template(
        "desktop/fixture/fixture.html",
        css_files=["rest_of_website.css", "iframe.css"],
        js_files=["fixture.js", "iframe.js"],
        fixture=fixture,
        match_report=match_report,
        home_club=fixture.club_x,
        away_club=fixture.club_y,
        home_players=home_players,
        away_players=away_players,
        reverse_fixture=reverse_fixture,
        recent_results=recent_results,
        pre_match_league_tables=pre_match_league_tables,
        post_match_league_tables=post_match_league_tables,
        num_clubs=len(universe.systems[0].leagues[0].clubs),
    )
