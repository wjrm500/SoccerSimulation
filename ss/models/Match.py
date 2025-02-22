import funcy
import numpy as np

from .. import goal_probability, utils
from .PlayerReportEngine import PlayerReportEngine


class Match:
    def __init__(self, fixture, tournament, date, club_x, club_y, neutral_venue=False):
        self.fixture = fixture
        self.tournament = tournament
        self.date = date
        self.club_x, self.club_y = club_x, club_y
        self.clubs = [self.club_x, self.club_y]
        self.neutral_venue = neutral_venue
        self.match_report = {
            "fixture_id": self.fixture.id,
            "tournament": self.tournament,
            "gameweek": self.fixture.gameweek,
            "date": self.date,
            "clubs": {club: {} for club in self.clubs},
        }
        report = self.match_report
        home_away_tuple = (None, None) if self.neutral_venue else ("home", "away")
        for club, home_away in zip(self.clubs, home_away_tuple):
            report["clubs"][club]["team"] = club.select_team(home_away=home_away)
        report["clubs"][self.club_x]["potential"] = (
            report["clubs"][self.club_x]["team"].offence
            - report["clubs"][self.club_y]["team"].defence
        )
        report["clubs"][self.club_y]["potential"] = (
            report["clubs"][self.club_y]["team"].offence
            - report["clubs"][self.club_x]["team"].defence
        )
        for club in self.clubs:
            opposition_club = self.get_opposition_club(club)
            report["clubs"][club]["opposition_club"] = funcy.omit(
                report["clubs"][opposition_club], "opposition_club"
            )

    def get_opposition_club(self, club):
        return self.clubs[1 - self.clubs.index(club)]

    def play(self):
        report = self.match_report
        for club in self.clubs:
            if report["clubs"][club]["team"] is None:
                continue
            report["clubs"][club]["match"] = {}
            potential = report["clubs"][club]["potential"]
            [mu, sigma] = list(goal_probability.goal_probability[int(potential)].values())
            goals_for = int(utils.limit_value(np.random.normal(mu, sigma), mn=0, mx=100))
            report["clubs"][club]["match"]["goals_for"] = goals_for
            report["clubs"][club]["match"]["goals"] = report["clubs"][club]["team"].get_goals(
                goals_for
            )
        for club in self.clubs:
            opposition_club = self.get_opposition_club(club)
            report["clubs"][club]["match"]["goals_against"] = report["clubs"][opposition_club][
                "match"
            ]["goals_for"]
            if (
                report["clubs"][club]["match"]["goals_for"]
                > report["clubs"][club]["match"]["goals_against"]
            ):
                report["clubs"][club]["match"]["outcome"] = "win"
                self.match_report["winner"] = club
            elif (
                report["clubs"][club]["match"]["goals_for"]
                == report["clubs"][club]["match"]["goals_against"]
            ):
                report["clubs"][club]["match"]["outcome"] = "draw"
            else:
                report["clubs"][club]["match"]["outcome"] = "loss"
        player_report_engine = PlayerReportEngine(self)
        player_report_engine.generate_player_reports(report)

    def file_match_report(self):
        self.fixture.handle_match_report(self.match_report)
        self.tournament.handle_match_report(self.match_report)
