import numpy as np

from .. import goal_probability, utils
from .match_models import MatchReport, TeamMatchReport
from .PlayerReportEngine import PlayerReportEngine


class Match:
    def __init__(self, fixture, league, date, club_x, club_y, neutral_venue=False):
        self.fixture = fixture
        self.league = league
        self.date = date
        self.club_x, self.club_y = club_x, club_y
        self.clubs = [self.club_x, self.club_y]
        self.neutral_venue = neutral_venue

        # Create teams
        home_away = (None, None) if self.neutral_venue else ("home", "away")
        x_team = club_x.select_team(home_away=home_away[0])
        y_team = club_y.select_team(home_away=home_away[1])

        # Create team match reports
        x_potential = x_team.offence - y_team.defence if x_team and y_team else 0
        y_potential = y_team.offence - x_team.defence if x_team and y_team else 0

        x_report = TeamMatchReport(team=x_team, potential=x_potential)
        y_report = TeamMatchReport(team=y_team, potential=y_potential)

        # Create match report
        self.match_report = MatchReport(
            fixture_id=self.fixture.id,
            league=self.league,
            gameweek=self.fixture.gameweek,
            match_date=self.date,
            home_club=self.club_x,
            away_club=self.club_y,
            home_report=x_report,
            away_report=y_report,
            neutral_venue=self.neutral_venue,
        )

    def get_opposition_club(self, club):
        return self.clubs[1 - self.clubs.index(club)]

    def play(self):
        report = self.match_report

        # Process each team's performance
        for team_report in report.clubs_reports.values():
            if team_report.team is None:
                continue

            potential = team_report.potential
            [mu, sigma] = list(goal_probability.goal_probability[int(potential)].values())
            goals_for = int(utils.limit_value(np.random.normal(mu, sigma), mn=0, mx=100))
            team_report.goals_for = goals_for
            team_report.goals = team_report.team.get_goals(goals_for)

        # Set goals against and determine outcome
        report.home_report.goals_against = report.away_report.goals_for
        report.away_report.goals_against = report.home_report.goals_for

        # Determine match outcomes
        for team_report in report.clubs_reports.values():
            if team_report.goals_for > team_report.goals_against:
                team_report.outcome = "win"
            elif team_report.goals_for == team_report.goals_against:
                team_report.outcome = "draw"
            else:
                team_report.outcome = "loss"

        # Generate player reports
        player_report_engine = PlayerReportEngine(self)
        player_report_engine.generate_player_reports(report)

    def file_match_report(self):
        self.fixture.handle_match_report(self.match_report)
        self.league.handle_match_report(self.match_report)
