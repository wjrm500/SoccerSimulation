import numpy as np

from .. import goal_probability, utils
from .dataclasses import PlayerReport


class PlayerReportEngine:
    """Engine for generating player performance reports after a match."""

    # Rating calculation constants
    RATING_SCALE = 5.0
    RATING_SIGMOID_DIVISOR = 12.5
    MIN_RATING = 2.5
    MAX_RATING = 7.5
    RATING_SIGMA = 0.5

    # Performance multipliers
    PERFORMANCE_MULTIPLIER = 5.0
    PERFORMANCE_MIN = -1.5
    PERFORMANCE_MAX = 1.5

    # Goal and assist factors
    ASSIST_VALUE_FACTOR = 0.75
    PREDICTED_ASSIST_FACTOR = 0.9

    # Fatigue calculation constants
    FITNESS_LIMIT = 35
    FITNESS_DIVISOR = 10
    FITNESS_EXPONENT = 2
    FITNESS_DENOMINATOR = 25
    FATIGUE_BASE = 0.25
    FATIGUE_SIGMA = 0.05
    MIN_FATIGUE = 0.05
    MAX_FATIGUE = 0.45

    # Form calculation
    FORM_GRAVITY_FACTOR = 0.1  # Player's form impact on new form (1/10)

    def __init__(self, match):
        """Initialise the engine with the match being processed."""
        self.match = match
        self.man_of_the_match = None

    def generate_player_reports(self, report):
        """Generate performance reports for all players in the match."""
        # Calculate mean fitness of all players in the match
        mean_fitness = self._calculate_mean_fitness(report)

        # Process reports for each club's players
        for club, team_report in report.clubs_reports.items():
            team = team_report.team
            for select in team.selection:
                player = select.player
                team_report.players[player] = self._generate_player_report(
                    club, team, select, mean_fitness
                )

        # Designate man of the match
        self._assign_man_of_the_match(report)

    def _calculate_mean_fitness(self, report):
        """Calculate the average fitness of all players in the match."""
        all_fitness_values = [
            select.player.skill_values["fitness"]
            for club in self.match.clubs
            for select in report.clubs_reports[club].team.selection
        ]
        return np.mean(all_fitness_values)

    def _assign_man_of_the_match(self, report):
        """Designate the best performer as man of the match."""
        if not self.man_of_the_match:
            return

        best_player = self.man_of_the_match["player"]
        for team_report in report.clubs_reports.values():
            for select in team_report.team.selection:
                player = select.player
                team_report.players[player].man_of_the_match = player == best_player

    def _generate_player_report(self, club, team, select, mean_fitness):
        """Generate a comprehensive performance report for a player."""
        player = select.player
        position = select.position

        # Get match context data
        opposition_club = self.match.get_opposition_club(club)
        club_report = self.match.match_report.clubs_reports[club]
        opposition_report = self.match.match_report.clubs_reports[opposition_club]

        # Calculate base player rating from skill difference
        rating_data = self._calculate_player_rating(select, club_report, opposition_report)

        # Calculate team performance and player contribution
        team_perf = self._calculate_team_performance(club_report, opposition_report)
        player_contrib = self._calculate_player_contribution(select, team, team_perf)

        # Calculate goal and assist contributions
        goal_assist_data = self._calculate_goal_assist_impact(
            player, team, club_report, opposition_report
        )

        # Calculate overall performance index
        performance_index = self._calculate_performance_index(
            rating_data, player_contrib, goal_assist_data
        )

        # Update man of the match if this is the best performance so far
        if (
            not self.man_of_the_match
            or performance_index > self.man_of_the_match["performance_index"]
        ):
            self.man_of_the_match = {"player": player, "performance_index": performance_index}

        # Calculate fatigue and form impact
        fatigue_increase = self._calculate_fatigue_increase(player, mean_fitness)
        form_change = self._calculate_form_change(
            player, performance_index, rating_data["base_rating"]
        )

        # Compile extra data for detailed analysis
        extra_data = self._create_extra_data_dict(rating_data, team_perf)

        # Create the final player report
        return PlayerReport(
            fixture_id=self.match.fixture.id,
            home_away="H" if self.match.club_x == player.club else "A",
            league=self.match.league,
            date=self.match.date,
            gameweek=self.match.fixture.gameweek,
            position=position,
            pre_match_form=player.form,
            goals=goal_assist_data["goals_scored"],
            assists=goal_assist_data["assists"],
            opposition_club=opposition_club,
            performance_index=performance_index,
            fatigue_increase=fatigue_increase,
            form_change=form_change,
            extra_data=extra_data,
        )

    def _calculate_player_rating(self, select, club_report, opposition_report):
        """Calculate the player's base rating based on skill differential."""
        # Get player and opposition ratings
        select_rating = club_report.team.get_select_rating(select)
        opposition_rating = opposition_report.team.average_rating
        rating_advantage = select_rating - opposition_rating

        # Apply sigmoid function to transform rating advantage to a 0-10 scale
        sigmoid_value = 1 / (1 + np.power(np.e, (-rating_advantage / self.RATING_SIGMOID_DIVISOR)))
        base_rating = (sigmoid_value + 0.5) * self.RATING_SCALE

        # Add some randomness to the base rating
        modulated_rating = utils.limited_rand_norm(
            {
                "mu": base_rating,
                "sg": self.RATING_SIGMA,
                "mn": self.MIN_RATING,
                "mx": self.MAX_RATING,
            }
        )

        return {
            "select_rating": select_rating,
            "opposition_team_rating": opposition_rating,
            "base_rating": base_rating,
            "modulated_base_rating": modulated_rating,
        }

    def _calculate_team_performance(self, club_report, opposition_report):
        """Calculate how the team performed relative to expectations."""
        # Offensive performance (goals scored vs expected)
        predicted_goals_for = utils.limit_value(
            goal_probability.goal_probability[int(club_report.potential)]["mu"], mn=0
        )
        actual_goals_for = club_report.goals_for
        offensive_outperformance = actual_goals_for - predicted_goals_for

        # Defensive performance (goals conceded vs expected)
        predicted_goals_against = utils.limit_value(
            goal_probability.goal_probability[int(opposition_report.potential)]["mu"], mn=0
        )
        actual_goals_against = opposition_report.goals_for
        defensive_outperformance = predicted_goals_against - actual_goals_against

        return {
            "actual_goals_for": actual_goals_for,
            "offensive_outperformance": offensive_outperformance,
            "actual_goals_against": actual_goals_against,
            "defensive_outperformance": defensive_outperformance,
        }

    def _calculate_player_contribution(self, select, team, team_perf):
        """Calculate how much the player contributed to team performance."""
        offensive_contribution = team.selection_offensive_contributions[select]
        defensive_contribution = team.selection_defensive_contributions[select]

        # Calculate performance boosts based on team over/underperformance
        # A player gets more credit for team success if they contributed more
        offensive_boost = utils.limit_value(
            offensive_contribution
            * team_perf["offensive_outperformance"]
            * self.PERFORMANCE_MULTIPLIER,
            mn=self.PERFORMANCE_MIN,
            mx=self.PERFORMANCE_MAX,
        )

        defensive_boost = utils.limit_value(
            defensive_contribution
            * team_perf["defensive_outperformance"]
            * self.PERFORMANCE_MULTIPLIER,
            mn=self.PERFORMANCE_MIN,
            mx=self.PERFORMANCE_MAX,
        )

        return {
            "offensive_contribution": offensive_contribution,
            "defensive_contribution": defensive_contribution,
            "offensive_boost": offensive_boost,
            "defensive_boost": defensive_boost,
        }

    def _calculate_goal_assist_impact(self, player, team, club_report, opposition_report):
        """Calculate the impact of goals and assists on player rating."""
        # Count actual goals and assists
        goals = club_report.goals or []
        goals_scored = sum(1 for goal in goals if goal.scorer == player)
        assists = sum(1 for goal in goals if goal.assister == player)

        # Get player's likelihood factors
        goal_likelihood = team.goal_factors[player]
        assist_likelihood = team.assist_factors[player]

        # Calculate match context values for rating boosts
        goal_difference = abs(club_report.goals_for - opposition_report.goals_for)
        total_goals = club_report.goals_for + opposition_report.goals_for

        # Calculate rating boosts for goals and assists
        goal_boost, assist_boost = self.get_rating_boosts_for_goals_and_assists(
            goal_difference, total_goals
        )

        # Expected and actual goal contributions
        team_predicted_goals = utils.limit_value(
            goal_probability.goal_probability[int(club_report.potential)]["mu"], mn=0
        )
        predicted_goals = team_predicted_goals * goal_likelihood
        goal_negative = predicted_goals * goal_boost / self.RATING_SCALE
        goal_positive = goals_scored * goal_boost

        # Expected and actual assist contributions
        predicted_assists = team_predicted_goals * self.PREDICTED_ASSIST_FACTOR * assist_likelihood
        assist_negative = predicted_assists * assist_boost / self.RATING_SCALE
        assist_positive = assists * assist_boost

        return {
            "goals_scored": goals_scored,
            "assists": assists,
            "predicted_goals": predicted_goals,
            "predicted_assists": predicted_assists,
            "goal_negative": goal_negative,
            "goal_positive": goal_positive,
            "assist_negative": assist_negative,
            "assist_positive": assist_positive,
        }

    def _calculate_performance_index(self, rating_data, player_contrib, goal_assist_data):
        """Calculate the overall performance index for the player."""
        # Combine all performance factors into a single index
        performance_index = utils.limit_value(
            rating_data["modulated_base_rating"]
            + player_contrib["offensive_boost"]
            + player_contrib["defensive_boost"]
            - goal_assist_data["goal_negative"]
            + goal_assist_data["goal_positive"]
            - goal_assist_data["assist_negative"]
            + goal_assist_data["assist_positive"],
            mn=0,
            mx=10,
        )

        return performance_index

    def _calculate_fatigue_increase(self, player, mean_fitness):
        """Calculate fatigue increase based on player's fitness relative to match average."""
        # How different is this player's fitness from the average?
        fitness_difference = utils.limit_value(
            player.skill_values["fitness"] - mean_fitness,
            mn=-self.FITNESS_LIMIT,
            mx=self.FITNESS_LIMIT,
        )

        # Calculate fatigue adjustment factors
        a = (
            np.power(abs(fitness_difference) / self.FITNESS_DIVISOR, self.FITNESS_EXPONENT)
            / self.FITNESS_DENOMINATOR
        )
        b = np.power(a, 1.5)

        # Better fitness = less fatigue, worse fitness = more fatigue
        if fitness_difference > 0:
            fatigue_mean = self.FATIGUE_BASE - a + b
        else:
            fatigue_mean = self.FATIGUE_BASE + a - b

        # Add randomness to fatigue calculation
        fatigue_increase = utils.limited_rand_norm(
            {
                "mu": fatigue_mean,
                "sg": self.FATIGUE_SIGMA,
                "mn": self.MIN_FATIGUE,
                "mx": self.MAX_FATIGUE,
            }
        )

        return fatigue_increase

    def _calculate_form_change(self, player, performance_index, base_rating):
        """Calculate the change on player's form from this match."""
        # Calculate how much better/worse player performed than expected
        outperformance = performance_index - base_rating

        # Convert to form scale
        ungravitated_form_change = outperformance / self.RATING_SCALE

        # Apply gravitational pull based on current form
        # High form pulls form down, low form pulls it up
        gravity = player.form * self.FORM_GRAVITY_FACTOR
        return ungravitated_form_change - gravity

    def _create_extra_data_dict(self, rating_data, team_perf):
        """Create a dictionary of extra data for detailed analysis."""
        return {
            "select_rating": rating_data["select_rating"],
            "team_actual_goals_for": team_perf["actual_goals_for"],
            "team_actual_goals_against": team_perf["actual_goals_against"],
        }

    def get_rating_boosts_for_goals_and_assists(self, goal_difference, goals_scored):
        """Calculate how valuable goals and assists are in this specific match context."""
        # Goal difference component: goals more valuable in close games
        if goal_difference == 0:
            goal_difference_component = 1.5
        else:
            goal_difference_component = 2.5 - np.power(goal_difference, 0.25)

        # Goals scored component: goals more valuable in low-scoring games
        if goals_scored == 0:
            goals_scored_component = 1.5
        else:
            goals_scored_component = 1.5 - (goals_scored - 1) * (3 / 40)

        # Combine components with 2:1 weighting for goal difference
        goal_boost = ((goal_difference_component * 2) + goals_scored_component) / 3

        # Assists worth 75% of goals
        assist_boost = goal_boost * self.ASSIST_VALUE_FACTOR

        return [goal_boost, assist_boost]
