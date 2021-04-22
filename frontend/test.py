import sys
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app")
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app\\models")
from Universe import Universe
from Database import Database
import os
import pickle

db = Database.getInstance()
universeKey = 'rdiqgqvycm'
universe = db.getUniverse(universeKey)
universe = pickle.loads(universe)
league = universe.systems[0].leagues[0]
# a = league.getPerformanceIndices(sortBy = 'performanceIndex')
scores = []
for matchReport in league.matchReports:
    clubA, clubB = matchReport['clubs'].keys()
    match = list(matchReport['clubs'].values())[0]['match']
    scoreA, scoreB = match['goalsFor'], match['goalsAgainst']
    scores.append({
        'date': matchReport['date'].strftime('%d-%m-%Y'),
        'homeClub': clubA,
        'awayClub': clubB,
        'homeScore': scoreA,
        'awayScore': scoreB
    })
a = 1