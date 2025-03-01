import copy

import numpy as np

from .. import config
from .Select import Select
from .Team import Team


class Club:
    def __init__(self, league, city):
        self.id = city["_id"]
        self.name = city["city_name"]
        self.league = league
        self.players = []
        num_players_per_club = (
            league.system.universe.config["num_players_per_club"]
            or config.system_config["num_players_per_club"]
        )
        for _ in range(num_players_per_club):
            player = self.league.system.universe.player_controller.create_player()
            self.players.append(player)
            player.club = self
            self.alter_player_rating_easter_egg(player)
        self.favourite_formation = self.set_favourite_formation()

    def alter_player_rating_easter_egg(self, player):
        if self.name in [
            "Arsenal",
            "Arsenal FC",
            "Gunners",
            "The Gunners",
            "Newcastle",
            "Newcastle United",
            "Newcastle United FC",
            "The Toon",
            "Toon Army",
        ]:
            player.peak_rating -= 10
            player.set_rating()
            player.set_skill_values()
            player.set_position_ratings()
        elif self.name in ["Liverpool", "Liverpool FC"]:
            player.peak_rating += 10
            player.set_rating()
            player.set_skill_values()
            player.set_position_ratings()

    def set_favourite_formation(self):
        formations, weights = [], []
        for key, value in config.formation_config.items():
            formations.append(key)
            weights.append(value["popularity"])
        return np.random.choice(formations, size=1, p=weights)[0]

    def select_team(self, home_away="neutral", squad=None, test=False):
        try:
            squad = self.players if squad is None else squad
            if len(squad) < 10:
                raise Exception("Not enough players to form a full team.")
            chosen_formation = self.favourite_formation
            personnel_required = copy.deepcopy(
                config.formation_config[chosen_formation]["personnel"]
            )
            selection = []
            while sum(personnel_required.values()) > 0:
                max_value = 0
                for position, num_players in personnel_required.items():
                    if num_players > 0:
                        for player in squad:
                            if (
                                player not in [select.player for select in selection]
                                and (False if test else player.injured) is False
                            ):
                                select_rating = player.position_ratings[position]
                                select_rating -= 0 if test else select_rating * player.fatigue
                                select_rating += 0 if test else (select_rating * player.form) / 10
                                select_rating *= config.match_config["home_away_differential"][
                                    home_away
                                ]
                                if select_rating > max_value:
                                    max_value = select_rating
                                    select = Select(player, position, select_rating)
                personnel_required[select.position] -= 1
                selection.append(select)
            return Team(self, chosen_formation, selection)
        except Exception:
            return None

    def get_rating(self, decimal_places=2):
        return round(np.mean([player.rating for player in self.players]), decimal_places)
