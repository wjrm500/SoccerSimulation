import numpy as np

from .. import goal_probability, utils
from .dataclasses import PlayerReport


class PlayerReportEngine:
    def __init__(self, match):
        self.match = match
        self.man_of_the_match = None

    def generate_player_reports(self, report):
        mean_fitness = np.mean(
            [
                select.player.skill_values["fitness"]
                for club in self.match.clubs
                for select in report.clubs_reports[club].team.selection
            ]
        )

        # Generate player reports for each club
        for club, team_report in report.clubs_reports.items():
            team = team_report.team
            for select in team.selection:
                player = select.player
                team_report.players[player] = self.get_player_report(
                    club, team, select, mean_fitness
                )

        # Tag man of the match
        man_of_the_match = self.man_of_the_match["player"]
        for team_report in report.clubs_reports.values():
            for select in team_report.team.selection:
                player = select.player
                team_report.players[player].man_of_the_match = player == man_of_the_match

    def get_player_report(self, club, team, select, mean_fitness):
        player = select.player
        position = select.position
        player_goal_likelihood = team.goal_factors[player]
        player_assist_likelihood = team.assist_factors[player]

        club = player.club
        opposition_club = self.match.get_opposition_club(club)
        club_report = self.match.match_report.clubs_reports[club]
        opposition_club_report = self.match.match_report.clubs_reports[opposition_club]
        goals = club_report.goals
        goals_scored = sum([1 for goal in goals if goal.scorer == player]) if goals else 0
        assists = sum([1 for goal in goals if goal.assister == player]) if goals else 0

        ### Get player performance index
        select = club_report.team.get_select_from_player(player)
        select_rating = club_report.team.get_select_rating(select)
        opposition_team_rating = opposition_club_report.team.average_rating
        rating_advantage = select_rating - opposition_team_rating
        x = rating_advantage
        base_rating = ((1 / (1 + np.power(np.e, (-x / 12.5)))) + 0.5) * 5
        modulated_base_rating = utils.limited_rand_norm(
            {"mu": base_rating, "sg": 0.5, "mn": 2.5, "mx": 7.5}
        )

        offensive_contribution = club_report.team.selection_offensive_contributions[select]
        defensive_contribution = club_report.team.selection_defensive_contributions[select]
        team_predicted_goals_for = utils.limit_value(
            goal_probability.goal_probability[int(club_report.potential)]["mu"], mn=0
        )
        team_actual_goals_for = club_report.goals_for
        team_offensive_outperformance = team_actual_goals_for - team_predicted_goals_for
        team_predicted_goals_against = utils.limit_value(
            goal_probability.goal_probability[int(opposition_club_report.potential)]["mu"],
            mn=0,
        )
        team_actual_goals_against = opposition_club_report.goals_for
        team_defensive_outperformance = team_predicted_goals_against - team_actual_goals_against
        offensive_boost = utils.limit_value(
            offensive_contribution * team_offensive_outperformance * 5, mn=-1.5, mx=1.5
        )
        defensive_boost = utils.limit_value(
            defensive_contribution * team_defensive_outperformance * 5, mn=-1.5, mx=1.5
        )

        goal_difference = abs(club_report.goals_for - opposition_club_report.goals_for)
        goals_scored_total = club_report.goals_for + opposition_club_report.goals_for
        rating_boost_for_goal, rating_boost_for_assist = (
            self.get_rating_boosts_for_goals_and_assists(goal_difference, goals_scored_total)
        )

        player_predicted_goals = team_predicted_goals_for * player_goal_likelihood
        goal_negative = player_predicted_goals * rating_boost_for_goal / 5
        goal_positive = goals_scored * rating_boost_for_goal

        player_predicted_assists = team_predicted_goals_for * 0.9 * player_assist_likelihood
        assist_negative = player_predicted_assists * rating_boost_for_assist / 5
        assist_positive = assists * rating_boost_for_assist

        performance_index = utils.limit_value(
            modulated_base_rating
            + offensive_boost
            + defensive_boost
            - goal_negative
            + goal_positive
            - assist_negative
            + assist_positive,
            mn=0,
            mx=10,
        )

        if (
            self.man_of_the_match is None
            or performance_index > self.man_of_the_match["performance_index"]
        ):
            self.man_of_the_match = {
                "player": player,
                "performance_index": performance_index,
            }

        ### Handle fatigue
        fitness_from_mean = utils.limit_value(
            player.skill_values["fitness"] - mean_fitness, mn=-35, mx=35
        )
        a = np.power(abs(fitness_from_mean) / 10, 2) / 25
        b = np.power(a, 1.5)
        if fitness_from_mean > 0:
            mu = 0.25 - a + b
        else:
            mu = 0.25 + a - b
        fatigue_increase = utils.limited_rand_norm({"mu": mu, "sg": 0.05, "mn": 0.05, "mx": 0.45})

        ### Handle form
        outperformance = performance_index - base_rating
        ungravitated_match_form = outperformance / 5
        gravity = player.form / 10
        gravitated_match_form = ungravitated_match_form - gravity

        ### Add extra data
        extra_data = {
            "select_rating": select_rating,
            "opposition_team_rating": opposition_team_rating,
            "base_rating": base_rating,
            "modulated_base_rating": modulated_base_rating,
            "offensive_contribution": offensive_contribution,
            "defensive_contribution": defensive_contribution,
            "team_predicted_goals_for": team_predicted_goals_for,
            "team_actual_goals_for": team_actual_goals_for,
            "team_offensive_outperformance": team_offensive_outperformance,
            "team_predicted_goals_against": team_predicted_goals_against,
            "team_actual_goals_against": team_actual_goals_against,
            "team_defensive_outperformance": team_defensive_outperformance,
            "offensive_boost": offensive_boost,
            "defensive_boost": defensive_boost,
            "predicted_goals": player_predicted_goals,
            "goal_negative": goal_negative,
            "goal_positive": goal_positive,
            "predicted_assists": player_predicted_assists,
            "assist_negative": assist_negative,
            "assist_positive": assist_positive,
        }

        return PlayerReport(
            fixture_id=self.match.fixture.id,
            home_away="H" if self.match.club_x == player.club else "A",
            league=self.match.league,
            date=self.match.date,
            gameweek=self.match.fixture.gameweek,
            position=position,
            pre_match_form=player.form,
            goals=goals_scored,
            assists=assists,
            opposition_club=opposition_club,
            performance_index=performance_index,
            fatigue_increase=fatigue_increase,
            ungravitated_match_form=ungravitated_match_form,
            gravitated_match_form=gravitated_match_form,
            extra_data=extra_data,
        )

    def get_rating_boosts_for_goals_and_assists(self, goal_difference, goals_scored):
        goal_difference_component_of_rating_boost_for_goal = (
            1.5 if goal_difference == 0 else 2.5 - np.power(goal_difference, (1 / 4))
        )
        goals_scored_component_of_rating_boost_for_goal = (
            1.5 if goals_scored == 0 else 1.5 - (goals_scored - 1) * (3 / 40)
        )
        rating_boost_for_goal = (
            (goal_difference_component_of_rating_boost_for_goal * 2)
            + goals_scored_component_of_rating_boost_for_goal
        ) / 3
        rating_boost_for_assist = rating_boost_for_goal * 0.75
        return [rating_boost_for_goal, rating_boost_for_assist]
