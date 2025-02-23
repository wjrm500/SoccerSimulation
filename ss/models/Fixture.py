from .Match import Match


class Fixture:
    def __init__(self, fixture_id, tournament, date=None, club_x=None, club_y=None):
        self.id = fixture_id
        self.tournament = tournament
        self.date = date
        self.add_clubs(club_x, club_y)

    def add_clubs(self, club_x, club_y):
        self.club_x, self.club_y = club_x, club_y
        self.clubs = [self.club_x, self.club_y]

    def set_gameweek(self, gameweek):
        self.gameweek = gameweek

    def play(self):
        self.match = Match(self, self.tournament, self.date, self.club_x, self.club_y)
        self.match.play()
        self.match.file_match_report()

    def handle_match_report(self, match_report):
        self.goals = {}
        club_x = list(match_report["clubs"].keys())[0]
        club_y = list(match_report["clubs"].keys())[1]
        self.goals[club_x] = match_report["clubs"][club_x]["match"]["goals_for"]
        self.goals[club_y] = match_report["clubs"][club_y]["match"]["goals_for"]
