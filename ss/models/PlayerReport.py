from datetime import date
from typing import Any


class PlayerReport:
    def __init__(
        self,
        fixture_id: int,
        home_away: str,
        tournament: Any,  # Tournament or Group
        date: date,
        gameweek: int,
        position: str,
        pre_match_fatigue: float,
        pre_match_form: float,
        goals: int,
        assists: int,
        opposition_club: Any,  # Club
        performance_index: float,
        fatigue_increase: float,
        ungravitated_match_form: float,
        gravitated_match_form: float,
        man_of_the_match: bool = False,
        extra_data: dict[str, Any] | None = None,
    ):
        self.fixture_id = fixture_id
        self.home_away = home_away
        self.tournament = tournament
        self.date = date
        self.gameweek = gameweek
        self.position = position
        self.pre_match_fatigue = pre_match_fatigue
        self.pre_match_form = pre_match_form
        self.goals = goals
        self.assists = assists
        self.opposition_club = opposition_club
        self.performance_index = performance_index
        self.fatigue_increase = fatigue_increase
        self.ungravitated_match_form = ungravitated_match_form
        self.gravitated_match_form = gravitated_match_form
        self.man_of_the_match = man_of_the_match
        self.extra_data = extra_data or {}
