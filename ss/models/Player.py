import copy
import random

import numpy as np

from .. import config, utils


def cosine_distance(u, v):
    # Compute cosine distance: 1 - cosine similarity
    dot = np.dot(u, v)
    norm_product = np.linalg.norm(u) * np.linalg.norm(v)
    return 1 - (dot / norm_product)


class Player:
    def __init__(self, controller, id):
        self.controller = controller
        self.id = id
        self.name = utils.generate_player_name()
        self.set_birth_date()
        self.set_age()
        self.retired = False
        self.set_peak_age()
        self.set_growth_speed()
        self.set_retirement_threshold()
        self.set_peak_rating()
        self.set_rating()
        self.set_underlying_skill_distribution()
        self.set_skill_distribution()
        self.set_skill_values()
        self.set_position_ratings()
        self.injured = False
        self.fatigue = 0
        self.player_reports = []
        self.injuries = []
        self.form = 0
        self.ratings = {}
        self.forms = {}

    def set_birth_date(self):
        agMin, agMax = (
            config.player_config["age"]["min"],
            config.player_config["age"]["max"],
        )
        age = random.randint(agMin, agMax)
        self.birth_date = utils.get_birth_date(config.time_config["start_date"], age)

    def get_age(self, dp=None):
        return round(self.age, dp) if dp is not None and dp > 0 else int(self.age)

    def get_age_on_date(self, date=None, dp=None):
        if date is None:
            return self.get_age(dp)
        td = date - self.birth_date
        age = td.days / 365.25
        return round(age, dp) if dp is not None and dp > 0 else int(age)

    def set_age(self):
        td = self.controller.universe.current_date - self.birth_date
        self.age = td.days / 365.25

    def set_peak_age(self):
        self.peak_age = utils.limited_rand_norm(config.player_config["peak_age"])

    def set_growth_speed(self):
        rand_incline = utils.limited_rand_norm(config.player_config["growth_speed"]["incline"])
        rand_decline = utils.limited_rand_norm(config.player_config["growth_speed"]["decline"])
        self.growth_speed = {"incline": rand_incline, "decline": rand_decline}

    def set_retirement_threshold(self):
        self.retirement_threshold = utils.limited_rand_norm(
            config.player_config["retirement_threshold"]
        )

    def set_peak_rating(self):
        d = config.player_config["peak_rating"]
        self.peak_rating = utils.limited_rand_norm(d)

    def adjust_peak_rating(self):
        mn, mx = (
            config.player_config["peak_rating"]["min"],
            config.player_config["peak_rating"]["max"],
        )
        self.peak_rating = utils.limited_rand_norm(
            {"mu": self.peak_rating, "sigma": 50 / (self.age**2), "mn": mn, "mx": mx}
        )

    def get_rating(self, age=None):
        age = self.age if age is None else age
        distance_from_peak_age = abs(self.peak_age - age)
        direction = "incline" if self.peak_age > age else "decline"
        growth_speed_factor = self.growth_speed[direction]
        peak_rating_fulfillment = 1 - (distance_from_peak_age**1.5 * 0.01 * growth_speed_factor)
        rating = self.peak_rating * peak_rating_fulfillment
        return rating

    def set_rating(self):
        self.rating = self.get_rating()
        direction = "incline" if self.peak_age > self.age else "decline"
        if (
            direction == "decline"
            and self.rating < (self.peak_rating * self.retirement_threshold)
            and self.retired is False
        ):
            self.retire()

    def rebalance_skill_distribution(self, distribution):
        [skDiMn, skDiMx] = list(list(config.player_config["skill"]["distribution"].values())[2:4])
        x = len(config.player_config["skill"]["skills"])
        while True:
            skills_out_of_bounds = []
            for value in distribution.values():
                if value < skDiMn or value > skDiMx:
                    skills_out_of_bounds.append(1)
                else:
                    skills_out_of_bounds.append(0)
            if not any(skills_out_of_bounds):
                break
            for key, value in distribution.items():
                distribution[key] = ((value * x) + len(distribution) - x) / len(distribution)
            x -= 0.1

    def set_underlying_skill_distribution(self):
        skills = config.player_config["skill"]["skills"]
        [skDiMu, skDiSg] = list(list(config.player_config["skill"]["distribution"].values())[0:2])
        underlying_skill_distribution = {
            skill: np.random.normal(skDiMu, skDiSg) for skill in skills
        }

        ### Centralise - set mean = 1
        total_skill = sum(underlying_skill_distribution.values())
        for key, value in underlying_skill_distribution.items():
            underlying_skill_distribution[key] = value * len(skills) / total_skill

        ### Rebalance - handle the passing of thresholds for minimum and maximum
        self.rebalance_skill_distribution(underlying_skill_distribution)

        self.underlying_skill_distribution = underlying_skill_distribution

    def get_skill_distribution(self, age=None):
        skill_distribution = copy.deepcopy(self.underlying_skill_distribution)

        ### Apply age-dependent modifications to distribution
        age = self.age if age is None else age
        transitions = config.player_config["skill"]["transitions"]
        distance_from_peak_age = self.peak_age - age
        for transition in transitions:
            direction = "incline" if self.peak_age > age else "decline"
            if (direction == "incline" and transition["when"]["incline"] is True) or (
                direction == "decline" and transition["when"]["decline"] is True
            ):
                if transition["from"] == "":
                    to_value = skill_distribution[transition["to"]]
                    to_factor = to_value / sum(skill_distribution.values())
                    modified_to_factor = to_factor - (
                        distance_from_peak_age * transition["gradient"]
                    )
                    skill_distribution[transition["to"]] = (
                        sum(skill_distribution.values()) * modified_to_factor
                    )
                elif transition["to"] == "":
                    from_value = skill_distribution[transition["from"]]
                    from_factor = from_value / sum(skill_distribution.values())
                    modified_from_factor = from_factor - (
                        distance_from_peak_age * transition["gradient"]
                    )
                    skill_distribution[transition["from"]] = (
                        sum(skill_distribution.values()) * modified_from_factor
                    )
                else:
                    from_value = skill_distribution[transition["from"]]
                    to_value = skill_distribution[transition["to"]]
                    from_to_sum = from_value + to_value
                    from_factor = from_value / from_to_sum
                    modified_from_factor = from_factor - (
                        distance_from_peak_age * transition["gradient"]
                    )
                    skill_distribution[transition["from"]] = from_to_sum * modified_from_factor
                    skill_distribution[transition["to"]] = from_to_sum * (1 - modified_from_factor)
                self.rebalance_skill_distribution(skill_distribution)

        ### Identify player's best position and normalise player's skill distribution towards the
        ### optimum for that position, to curb excessive weirdness
        best_position = self.get_best_position(skill_distribution)
        best_skill_distribution = config.player_config["positions"][best_position][
            "skill_distribution"
        ]
        normalising_factor = config.player_config["skill"]["normalising_factor"]
        for skill in skill_distribution.keys():
            skill_distribution[skill] = skill_distribution[skill] + (
                best_skill_distribution[skill] - skill_distribution[skill]
            ) * utils.limited_rand_norm(normalising_factor)

        ### Centralise - restore mean to 1
        total_skill = sum(skill_distribution.values())
        for key, value in skill_distribution.items():
            skill_distribution[key] = value * len(skill_distribution.values()) / total_skill

        return skill_distribution

    def set_skill_distribution(self):
        self.skill_distribution = self.get_skill_distribution()

    def get_skill_values(self, rating=None, skill_distribution=None):
        rating = self.rating if rating is None else rating
        skill_distribution = (
            self.skill_distribution if skill_distribution is None else skill_distribution
        )
        skill_values = {skill: rating * value for skill, value in skill_distribution.items()}
        return skill_values

    def set_skill_values(self):
        self.skill_values = self.get_skill_values()

    def get_position_suitabilities(self, skill_distribution=None):
        positions = config.player_config["positions"]
        skill_distribution = (
            self.skill_distribution if skill_distribution is None else skill_distribution
        )
        position_suitabilities = {}
        self_skill_distribution = list(skill_distribution.values())
        for position, attributes in positions.items():
            ideal_skill_distribution_for_position = list(attributes["skill_distribution"].values())
            position_suitability = 1 - cosine_distance(
                self_skill_distribution, ideal_skill_distribution_for_position
            )
            position_suitability = 1 - np.power(1 - position_suitability, (2 / 3))
            position_suitabilities[position] = position_suitability
        max_position_suitability = max(position_suitabilities.values())
        for position in position_suitabilities.keys():
            position_suitabilities[position] *= 1 / max_position_suitability
        return position_suitabilities

    def get_best_position(self, skill_distribution=None):
        position_suitabilities = (
            self.get_position_suitabilities()
            if skill_distribution is None
            else self.get_position_suitabilities(skill_distribution)
        )
        best_position = max(position_suitabilities, key=position_suitabilities.get)
        return best_position

    def get_position_ratings(self, rating=None, skill_distribution=None):
        rating = self.rating if rating is None else rating
        skill_distribution = (
            self.skill_distribution if skill_distribution is None else skill_distribution
        )
        position_suitabilities = self.get_position_suitabilities(skill_distribution)
        position_ratings = {
            position: rating * value for position, value in position_suitabilities.items()
        }
        return position_ratings

    def set_position_ratings(self):
        self.position_ratings = self.get_position_ratings()

    def recover(self):
        fatigue_reduction = np.sqrt(self.skill_values["fitness"]) / 100
        self.fatigue -= fatigue_reduction
        self.fatigue = 0 if self.fatigue < 0 else self.fatigue
        if self.injured:
            self.injured -= 1
        if self.injured == 0:
            self.injured = False
        self.form -= self.form / 25

    def injure(self):
        if self.club is not None and self.injured is False:
            injury = True if np.random.normal(self.fatigue, 0.25) > 0.75 else False
            if injury:
                x, item_array, probability_array = 1, [], []
                for i in range(1, 366):
                    x /= 1.05
                    item_array.append(i)
                    probability_array.append(x)
                probability_array = [
                    probability / sum(probability_array) for probability in probability_array
                ]
                injury_length = np.random.choice(item_array, p=probability_array)
                self.injured = injury_length
                self.injuries.append([self.club.league.system.universe.current_date, injury_length])

    def advance(self):
        self.injure()
        self.set_age()
        self.recover()
        self.adjust_peak_rating()
        self.set_rating()
        self.set_skill_distribution()
        self.set_skill_values()
        self.set_position_ratings()
        self.store_ratings_and_form()

    def handle_player_report(self, player_report):
        if (
            player_report not in self.player_reports
        ):  ### Prevent duplication from Universal Tournament group stage matches, which are handled
            ### by both the group and the wider tournament
            self.player_reports.append(player_report)
            self.fatigue += player_report["fatigue_increase"]
            self.form += player_report["gravitated_match_form"]

    def get_player_reports(self, gameweek=None):
        if gameweek is None:
            return self.player_reports
        return [
            player_report
            for player_report in self.player_reports
            if player_report["gameweek"] <= gameweek
        ]

    def get_proper_name(self, forename_style="Whole", surname_style="Whole"):
        ### Both forename_style and surname_style arguments can be set to either 'Empty',
        ### 'Shortened' or 'Whole'
        forename, surname = self.name[0], self.name[1]
        proper_name_array = []
        for style, name in zip([forename_style, surname_style], [forename, surname]):
            if style == "Shortened":
                proper_name_array.append(name[0] + ".")
            elif style == "Whole":
                proper_name_array.append(name)
        return " ".join(proper_name_array)

    def get_club_specific_name(self):
        other_players_at_club = [player for player in self.club.players if player != self]
        unique_surname = (
            len(list(filter(lambda x: self.name[1] == x.name[1], other_players_at_club))) == 0
        )
        return self.get_proper_name("Shortened" if not unique_surname else "")

    def retire(self):
        self.retired = True
        self.controller.retire_player(self)
        if hasattr(self, "club") and self.club:
            self.club.players.remove(self)
            self.club = None

    def store_ratings_and_form(self):
        current_date = self.controller.universe.current_date
        self.ratings[current_date] = {}
        self.ratings[current_date]["rating"] = self.rating
        self.ratings[current_date]["peak_rating"] = self.peak_rating
        self.forms[current_date] = self.form
