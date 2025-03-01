from .Match import Match


class Fixture:
    def __init__(self, fixture_id, league, date=None, club_x=None, club_y=None):
        self.id = fixture_id
        self.league = league
        self.date = date
        self.add_clubs(club_x, club_y)

    def add_clubs(self, club_x, club_y):
        self.club_x, self.club_y = club_x, club_y
        self.clubs = [self.club_x, self.club_y]

    def set_gameweek(self, gameweek):
        self.gameweek = gameweek

    def play(self):
        self.match = Match(self, self.league, self.date, self.club_x, self.club_y)
        self.match.play()
        self.match.file_match_report()

    def handle_match_report(self, match_report):
        self.goals = {}
        self.goals[match_report.home_club] = match_report.home_report.goals_for
        self.goals[match_report.away_club] = match_report.away_report.goals_for
