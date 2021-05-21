from config import systemConfig
from Club import Club
import copy
from Database import Database
import numpy as np

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
    
    def getLeagueTable(self, gameweek = None):
        if gameweek is None:
            gameweek = (len(self.clubs) - 1) * 2
        return self.leagueTables[gameweek]
    
    def getPerformanceIndices(
        self,
        indices = ['games', 'goals', 'assists', 'performanceIndex'],
        upToGameweek = None,
        sortBy = None,
        sortDir = None,
        clubs = None
        ):
        performanceIndices = {}
        clubs = clubs if clubs is not None else self.clubs
        clubs = clubs if type(clubs) == list else [clubs]
        upToGameweek = len(self.clubs) * 2 - 1 if upToGameweek is None else upToGameweek
        for club in clubs:
            club = self.system.universe.getClubByName(club) if type(club) == str else club
            for player in club.players:
                gamesPlayed = np.sum([1 for playerReport in player.playerReports if playerReport['tournament'] == self and playerReport['gameweek'] <= upToGameweek])
                performanceIndices[player] = {}
                if 'rating' in indices:
                    performanceIndices[player]['rating'] = player.rating
                if 'games' in indices:
                    performanceIndices[player]['games'] = int(gamesPlayed)
                if 'goals' in indices:
                    goals = np.sum([playerReport['goals'] for playerReport in player.playerReports if playerReport['tournament'] == self and playerReport['gameweek'] <= upToGameweek])
                    performanceIndices[player]['goals'] = int(goals)
                if 'assists' in indices:
                    assists = np.sum([playerReport['assists'] for playerReport in player.playerReports if playerReport['tournament'] == self and playerReport['gameweek'] <= upToGameweek])
                    performanceIndices[player]['assists'] = int(assists)
                if 'performanceIndex' in indices:
                    performanceIndex = np.mean([playerReport['performanceIndex'] for playerReport in player.playerReports if playerReport['tournament'] == self and playerReport['gameweek'] <= upToGameweek])
                    performanceIndices[player]['performanceIndex'] = round(performanceIndex, 2)
                    ### If player has appeared in less than half of the games they are ineligible for Performance Index ranking
                    if np.isnan(performanceIndices[player]['performanceIndex']): ### or gamesPlayed < upToGameweek / 2
                        performanceIndices[player]['performanceIndex'] = 0
                if 'positions' in indices:
                    performanceIndices[player]['positions'] = {position: [playerReport['position'] for playerReport in player.playerReports if playerReport['tournament'] == self and playerReport['gameweek'] <= upToGameweek].count(position) for position in set([playerReport['position'] for playerReport in player.playerReports if playerReport['tournament'] == self and playerReport['gameweek'] <= upToGameweek])}
        if sortBy is not None:
            sortedList = sorted(performanceIndices.items(), key = lambda x: x[1][sortBy], reverse = False if sortDir == 'asc' else True)
            performanceIndices = {player: performanceIndices for player, performanceIndices in sortedList}
        return performanceIndices