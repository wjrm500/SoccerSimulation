from goalProbability import goalProbability
import numpy as np
import Utils
import funcy
from PlayerReportEngine import PlayerReportEngine

class Match:
    def __init__(self, fixture, tournament, date, clubX, clubY, neutralVenue = False):
        self.fixture = fixture
        self.tournament = tournament
        self.date = date
        self.clubX, self.clubY = clubX, clubY
        self.clubs = [self.clubX, self.clubY]
        self.neutralVenue = neutralVenue
        self.matchReport = {'tournament': self.tournament, 'date': self.date, 'clubs': {club: {} for club in self.clubs}}
        report = self.matchReport
        homeAwayTuple = (None, None) if self.neutralVenue else ('Home', 'Away')
        for club, homeAway in zip(self.clubs, homeAwayTuple):
            report['clubs'][club]['team'] = club.selectTeam(homeAway = homeAway)
        report['clubs'][self.clubX]['potential'] = report['clubs'][self.clubX]['team'].offence - report['clubs'][self.clubY]['team'].defence
        report['clubs'][self.clubY]['potential'] = report['clubs'][self.clubY]['team'].offence - report['clubs'][self.clubX]['team'].defence
        clubXPot = report['clubs'][self.clubX]['potential']
        clubYPot = report['clubs'][self.clubY]['potential']  
        for club in self.clubs:
            oppositionClub = self.getOppositionClub(club)
            report['clubs'][club]['oppositionClub'] = funcy.omit(report['clubs'][oppositionClub], 'oppositionClub')

    def getOppositionClub(self, club):
        return self.clubs[1 - self.clubs.index(club)]

    def play(self):
        report = self.matchReport
        for club in self.clubs:
            if report['clubs'][club]['team'] == None:
                continue
            report['clubs'][club]['match'] = {}
            potential = report['clubs'][club]['potential']
            [mu, sigma] = [value for value in goalProbability[int(potential)].values()]
            goalsFor = int(Utils.limitValue(np.random.normal(mu, sigma), mn = 0, mx = 100))
            report['clubs'][club]['match']['goalsFor'] = goalsFor
            report['clubs'][club]['match']['goals'] = report['clubs'][club]['team'].getGoals(goalsFor)
        for club in self.clubs:
            oppositionClub = self.getOppositionClub(club)
            report['clubs'][club]['match']['goalsAgainst'] = report['clubs'][oppositionClub]['match']['goalsFor']
            if report['clubs'][club]['match']['goalsFor'] > report['clubs'][club]['match']['goalsAgainst']:
                report['clubs'][club]['match']['outcome'] = 'win'
                self.matchReport['winner'] = club
            elif report['clubs'][club]['match']['goalsFor'] == report['clubs'][club]['match']['goalsAgainst']:
                report['clubs'][club]['match']['outcome'] = 'draw'
            else:
                report['clubs'][club]['match']['outcome'] = 'loss'
        playerReportEngine = PlayerReportEngine(self)
        playerReportEngine.generatePlayerReports(report)

    def fileMatchReport(self):
        self.fixture.handleMatchReport(self.matchReport)
        self.tournament.handleMatchReport(self.matchReport)