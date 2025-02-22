import copy

import numpy as np

from ..config import system_config
from .Club import Club
from .Database import Database


class League:
    def __init__(self, system):
        self.system = system
        self.clubs = []
        self.league_tables = {0: {}}
        self.populate_with_clubs()
        self.match_reports = []

    def populate_with_clubs(self):
        db = Database.get_instance()
        num_clubs_per_league = (
            self.system.universe.config["num_clubs_per_league"]
            or system_config["num_clubs_per_league"]
        )
        cities = db.cnx["soccersim"]["cities"].aggregate(
            [
                {"$match": {"system_id": self.system.id}},
                {"$sample": {"size": num_clubs_per_league}},
            ]
        )
        cities = list(cities)
        custom_clubs = self.system.universe.config["custom_clubs"]
        if len(custom_clubs) > 0:
            for i, custom_club in enumerate(custom_clubs, 0):
                customCity = {
                    "_id": 1_000_000 + i,
                    "system_id": self.system.id,
                    "city_name": custom_club,
                }
                cities.insert(0, customCity)
                cities.pop()
        for city in cities:
            club = Club(self, city)
            self.clubs.append(club)
            self.league_tables[0][club] = {}
            for stat in ["GP", "W", "D", "L", "GF", "GA", "GD", "Pts"]:
                self.league_tables[0][club][stat] = 0

    def play_outstanding_fixtures(self, date):
        for fixture in self.fixtures:
            if fixture.date == date:
                fixture.play()

    def handle_match_report(self, match_report):
        self.match_reports.append(match_report)
        for club_report in match_report["clubs"].values():
            for player, player_report in club_report["players"].items():
                player.handle_player_report(player_report)
        max_games_played = max(self.league_tables.keys())
        gameweek_progression = (
            len({value["GP"] for value in self.league_tables[max_games_played].values()}) == 1
        )
        if gameweek_progression:
            current_gameweek = max_games_played + 1
            self.league_tables[current_gameweek] = {
                club: copy.deepcopy(self.league_tables[max_games_played][club])
                for club in self.clubs
            }
        else:
            current_gameweek = max_games_played
        for club, club_report in match_report["clubs"].items():
            self.league_tables[current_gameweek][club]["GP"] += 1
            self.league_tables[current_gameweek][club]["GF"] += club_report["match"]["goals_for"]
            self.league_tables[current_gameweek][club]["GA"] += club_report["match"][
                "goals_against"
            ]
            self.league_tables[current_gameweek][club]["GD"] += (
                club_report["match"]["goals_for"] - club_report["match"]["goals_against"]
            )
            if club_report["match"]["outcome"] == "win":
                self.league_tables[current_gameweek][club]["W"] += 1
                self.league_tables[current_gameweek][club]["Pts"] += 3
            elif club_report["match"]["outcome"] == "draw":
                self.league_tables[current_gameweek][club]["D"] += 1
                self.league_tables[current_gameweek][club]["Pts"] += 1
            elif club_report["match"]["outcome"] == "loss":
                self.league_tables[current_gameweek][club]["L"] += 1

    def get_league_table(self, gameweek=None):
        if gameweek is None:
            gameweek = (len(self.clubs) - 1) * 2
        return self.league_tables[gameweek]

    def get_performance_indices(
        self,
        indices=None,
        gameweek=None,
        sort_by=None,
        sort_dir=None,
        clubs=None,
    ):
        if indices is None:
            indices = ["games", "goals", "assists", "mvps", "performance_index"]
        performance_indices = {}
        clubs = clubs if clubs is not None else self.clubs
        clubs = clubs if isinstance(clubs, list) else [clubs]
        gameweek = gameweek or (len(self.clubs) - 1) * 2
        for club in clubs:
            club = self.system.universe.get_club_by_name(club) if isinstance(club, str) else club
            for player in club.players:
                games_played = np.sum(
                    [
                        1
                        for player_report in player.player_reports
                        if player_report["tournament"] == self
                        and player_report["gameweek"] <= gameweek
                    ]
                )
                performance_indices[player] = {}
                if "rating" in indices:
                    performance_indices[player]["rating"] = player.rating
                if "games" in indices:
                    performance_indices[player]["games"] = int(games_played)
                if "goals" in indices:
                    goals = np.sum(
                        [
                            player_report["goals"]
                            for player_report in player.player_reports
                            if player_report["tournament"] == self
                            and player_report["gameweek"] <= gameweek
                        ]
                    )
                    performance_indices[player]["goals"] = int(goals)
                if "assists" in indices:
                    assists = np.sum(
                        [
                            player_report["assists"]
                            for player_report in player.player_reports
                            if player_report["tournament"] == self
                            and player_report["gameweek"] <= gameweek
                        ]
                    )
                    performance_indices[player]["assists"] = int(assists)
                if "mvps" in indices:
                    mvps = np.sum(
                        [
                            player_report["man_of_the_match"]
                            for player_report in player.player_reports
                            if player_report["tournament"] == self
                            and player_report["gameweek"] <= gameweek
                        ]
                    )
                    performance_indices[player]["mvps"] = int(mvps)
                if "performance_index" in indices:
                    performance_index = np.mean(
                        [
                            player_report["performance_index"]
                            for player_report in player.player_reports
                            if player_report["tournament"] == self
                            and player_report["gameweek"] <= gameweek
                        ]
                    )
                    performance_indices[player]["performance_index"] = round(performance_index, 2)
                    ### If player has appeared in less than half of the games they are ineligible
                    ### for Performance Index ranking
                    if np.isnan(
                        performance_indices[player]["performance_index"]
                    ):  ### or games_played < gameweek / 2
                        performance_indices[player]["performance_index"] = 0
                if "positions" in indices:
                    performance_indices[player]["positions"] = {
                        position: [
                            player_report["position"]
                            for player_report in player.player_reports
                            if player_report["tournament"] == self
                            and player_report["gameweek"] <= gameweek
                        ].count(position)
                        for position in {
                            player_report["position"]
                            for player_report in player.player_reports
                            if player_report["tournament"] == self
                            and player_report["gameweek"] <= gameweek
                        }
                    }
        if sort_by is not None:
            sorted_list = sorted(
                performance_indices.items(),
                key=lambda x: x[1][sort_by],
                reverse=False if sort_dir == "asc" else True,
            )
            performance_indices = dict(sorted_list)
        return performance_indices
