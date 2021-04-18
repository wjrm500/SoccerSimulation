from config import systemConfig
from Club import Club
import copy
from Database import Database

class League:   
    def __init__(self, system):
        self.system = system
        self.clubs = []
        self.leagueTables = {0: {}}
        self.populateWithClubs()
        self.matchReports = []
    
    def populateWithClubs(self):
        db = Database.getInstance()
        cities = db.cnx['soccersim']['cities'].aggregate([
            {'$match': {'system_id': self.system.id}},
            {'$sample': {'size': systemConfig['numClubsPerLeague']}}
        ])
        # cities = db.cnx['soccersim']['cities'].find({
        #     'system_id': self.system.id
        # }).limit(systemConfig['numClubsPerLeague'])
        for city in cities:
            club = Club(self, city)
            self.clubs.append(club)
            self.leagueTables[0][club] = {}
            for stat in ['GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']:
                self.leagueTables[0][club][stat] = 0
    
    def playOutstandingFixtures(self, date):
        for fixture in self.fixtures:
            if fixture.date == date:
                fixture.play()
    
    def handleMatchReport(self, matchReport):
        self.matchReports.append(matchReport)
        for club, clubReport in matchReport['clubs'].items():
            for player, playerReport in clubReport['players'].items():
                player.handlePlayerReport(playerReport)
        maxGamesPlayed = max(self.leagueTables.keys())
        gameweekProgression = len(set([value['GP'] for value in self.leagueTables[maxGamesPlayed].values()])) == 1
        if gameweekProgression:
            currentGameweek = maxGamesPlayed + 1
            self.leagueTables[currentGameweek] = {club: copy.deepcopy(self.leagueTables[maxGamesPlayed][club]) for club in self.clubs}
        else:
            currentGameweek = maxGamesPlayed
        for club, clubReport in matchReport['clubs'].items():
            self.leagueTables[currentGameweek][club]['GP'] += 1
            self.leagueTables[currentGameweek][club]['GF'] += clubReport['match']['goalsFor']
            self.leagueTables[currentGameweek][club]['GA'] += clubReport['match']['goalsAgainst']
            self.leagueTables[currentGameweek][club]['GD'] += clubReport['match']['goalsFor'] - clubReport['match']['goalsAgainst']
            if clubReport['match']['outcome'] == 'win':
                self.leagueTables[currentGameweek][club]['W'] += 1
                self.leagueTables[currentGameweek][club]['Pts'] += 3
            elif clubReport['match']['outcome'] == 'draw':
                self.leagueTables[currentGameweek][club]['D'] += 1
                self.leagueTables[currentGameweek][club]['Pts'] += 1
            elif clubReport['match']['outcome'] == 'loss':
                self.leagueTables[currentGameweek][club]['L'] += 1
    
    def getLeagueTable(self, gameweek = 38):
        return self.leagueTables[gameweek]