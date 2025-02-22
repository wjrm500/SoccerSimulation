import copy
import re

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

    def get_provisional_short_name(self, precedence=0):
        ### If precedence = 0, use all available consonants
        ### If precedence = 1, ignore third consonant
        ### If precedence = 2, ignore third and fourth consonants
        ### Etc.
        first_letter_and_consonants_only = self.name[0] + re.sub(
            r"(?i)[aeiou -\.,]", "", self.name[1:]
        )
        provisional_short_name = (
            first_letter_and_consonants_only[: precedence + 3]
            if len(first_letter_and_consonants_only) >= precedence + 3
            else self.name[:3]
        ).upper()
        provisional_short_name = provisional_short_name[:2] + provisional_short_name[-1:]
        return provisional_short_name

    def get_short_name(self):
        ### Need to ensure no short name clashes with clubs in same league
        ### Basic idea is that clubs with higher ratings receive higher precedence when it comes to
        ### "naming rights". So we find all clubs in league whose provisional short names clash
        ### initially. Then we see where this particular club ranks amongst this set of clashing
        ### clubs. We then feed this rank as the argument to precedence in the
        ### get_provisional_short_name method
        short_name = self.get_provisional_short_name()
        clashing_clubs = []
        for club in self.league.clubs:
            if short_name == club.get_provisional_short_name():
                clashing_clubs.append(club)
        self_rank_among_clashing_clubs = sorted(
            clashing_clubs, key=lambda x: x.get_rating(), reverse=True
        ).index(self)
        return self.get_provisional_short_name(precedence=self_rank_among_clashing_clubs)

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

    def get_match_reports(self, gameweek=None):
        match_reports = [
            match_report
            for match_report in self.league.match_reports
            if self in match_report["clubs"]
        ]
        if gameweek is None:
            return match_reports
        return [
            match_report for match_report in match_reports if match_report["gameweek"] <= gameweek
        ]
