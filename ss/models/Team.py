import random

import numpy as np

from .. import config
from .dataclasses import Goal


class Team:
    ### Definitions
    ### Noun 'Select' - An entity comprising a player and a position, binded as a tuple
    ### Noun 'Selection' - An array or collection of Selects
    ### Noun 'Team' - A superlative entity whose values arise from the aggregation of values in a
    ### Selection
    def __init__(self, club, formation, selection):
        self.club = club
        self.formation = formation
        self.selection = selection
        self.select_ratings = {}
        self.players = [select.player for select in selection]
        self.set_average_rating()
        self.normalise_select_ratings()
        self.set_selection_offences_defences()
        self.set_team_offence_defence()
        self.set_selection_offensive_defensive_contributions()
        self.set_goal_and_assist_factors()

    def get_select_rating(self, select):
        return select.rating

    def set_average_rating(self):
        self.average_rating = np.mean(list(map(self.get_select_rating, self.selection)))

    def normalise_select_ratings(self):
        for select, select_rating in self.select_ratings.items():
            self.select_ratings[select] = ((select_rating * 2) + (self.average_rating * 1)) / 3

    def get_position_offence_defence(self, position):
        position_offence, position_defence = 0, 0
        for skill, value in config.player_config["positions"][position][
            "skill_distribution"
        ].items():
            position_offence += value * config.match_config["contribution"][skill]["offence"]
            position_defence += value * config.match_config["contribution"][skill]["defence"]
        position_offence /= 3
        position_defence /= 3
        return {"offence": position_offence, "defence": position_defence}

    def get_select_offence_defence(self, select):
        player = select.player
        position = select.position
        position_offence_defence = self.get_position_offence_defence(position)
        select_rating = self.get_select_rating(select)
        select_offence, select_defence = 0, 0
        for skill, value in player.skill_distribution.items():
            select_offence += (
                (value * select_rating)
                / 30
                * config.match_config["contribution"][skill]["offence"]
                * position_offence_defence["offence"]
            )
            select_defence += (
                (value * select_rating)
                / 30
                * config.match_config["contribution"][skill]["defence"]
                * position_offence_defence["defence"]
            )
        return {"offence": select_offence, "defence": select_defence}

    def set_selection_offences_defences(self):
        self.selection_offences, self.selection_defences = {}, {}
        for select in self.selection:
            select_offence_defence = self.get_select_offence_defence(select)
            self.selection_offences[select] = select_offence_defence["offence"]
            self.selection_defences[select] = select_offence_defence["defence"]

    def set_team_offence_defence(self):
        self.offence, self.defence = 0, 0
        for select in self.selection:
            self.offence += self.selection_offences[select]
            self.defence += self.selection_defences[select]

    def get_select_offensive_defensive_contribution(self, select):
        select_offence, select_defence = (
            self.selection_offences[select],
            self.selection_defences[select],
        )
        team_offence, team_defence = self.offence, self.defence
        return {
            "offensive": select_offence / team_offence,
            "defensive": select_defence / team_defence,
        }

    def set_selection_offensive_defensive_contributions(self):
        self.selection_offensive_contributions, self.selection_defensive_contributions = (
            {},
            {},
        )
        for select in self.selection:
            select_offensive_defensive_contribution = (
                self.get_select_offensive_defensive_contribution(select)
            )
            self.selection_offensive_contributions[select] = (
                select_offensive_defensive_contribution["offensive"]
            )
            self.selection_defensive_contributions[select] = (
                select_offensive_defensive_contribution["defensive"]
            )

    def get_goals(self, num_goals):
        if num_goals == 0:
            return
        return sorted([self.get_goal() for i in range(num_goals)], key=lambda x: x.minute)

    def set_goal_and_assist_factors(self):
        self.set_goal_factors()
        self.set_assist_factors()

    def set_goal_factors(self):
        goal_factors = {}
        for select in self.selection:
            position = select.position
            player = select.player
            select_rating = self.get_select_rating(select)
            goal_factor = (
                (
                    (
                        (player.skill_distribution["offence"] * 2)
                        + player.skill_distribution["technique"]
                    )
                    / 3
                )
                * select_rating
                * config.match_config["goal_likelihood"][position]
            ) ** 2
            goal_factors[player] = goal_factor
        sum_goal_factors = sum(goal_factors.values())
        self.goal_factors = {
            player: goal_factor / sum_goal_factors for player, goal_factor in goal_factors.items()
        }

    def set_assist_factors(self):
        assist_factors = {}
        for select in self.selection:
            position = select.position
            player = select.player
            select_rating = self.get_select_rating(select)
            assist_factor = (
                (
                    (
                        (
                            (player.skill_distribution["spark"] * 2)
                            + player.skill_distribution["technique"]
                        )
                        / 3
                    )
                    * select_rating
                    * config.match_config["assistLikelihood"][position]
                )
                ** 1.5
            )  ### The higher this number at the end, the less evenly distributed the assisters
            assist_factors[player] = assist_factor
        sum_assist_factors = sum(assist_factors.values())
        self.assist_factors = {
            player: assist_factor / sum_assist_factors
            for player, assist_factor in assist_factors.items()
        }

    def get_goal(self):
        scorer = self.get_goal_scorer()
        while True:
            assister = self.get_goal_assister()
            if assister != scorer:
                break
        minute = self.get_goal_minute()
        return Goal(scorer=scorer, assister=assister, minute=minute)

    def get_goal_scorer(self):
        goalscorer = np.random.choice(
            list(self.goal_factors.keys()), p=list(self.goal_factors.values())
        )
        return goalscorer

    def get_goal_assister(self):
        if np.random.choice([0, 1], p=[0.1, 0.9]) == 0:  ### Only 90% of goals are assisted
            return
        assister = np.random.choice(
            list(self.assist_factors.keys()), p=list(self.assist_factors.values())
        )
        return assister

    def get_goal_minute(self):
        return random.randint(1, 90)
