from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .Club import Club
    from .League import League
    from .Player import Player
    from .Team import Team


class MatchOutcome(Enum):
    WIN = "win"
    DRAW = "draw"
    LOSS = "loss"


@dataclass
class Goal:
    minute: int
    scorer: Player
    assister: Player | None = None


@dataclass
class PlayerReport:
    fixture_id: int
    home_away: str
    league: League
    date: date
    gameweek: int
    position: str
    pre_match_form: float
    goals: int
    assists: int
    opposition_club: Club
    performance_index: float
    fatigue_increase: float
    gravitated_match_form: float
    man_of_the_match: bool = False
    extra_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamMatchReport:
    team: Team
    potential: float
    goals_for: int = 0
    goals_against: int = 0
    outcome: MatchOutcome | None = None
    goals: list[Goal] = field(default_factory=list)
    players: dict[Player, PlayerReport] = field(default_factory=dict)


@dataclass
class MatchReport:
    fixture_id: int
    league: League
    gameweek: int
    match_date: date
    home_club: Club
    away_club: Club
    home_report: TeamMatchReport
    away_report: TeamMatchReport
    neutral_venue: bool = False

    @property
    def clubs_reports(self) -> dict[Club, TeamMatchReport]:
        return {self.home_club: self.home_report, self.away_club: self.away_report}
