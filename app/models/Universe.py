import config
from System import System
from Scheduler import Scheduler
import datetime
from PlayerController import PlayerController

class _Universe:
    def __init__(self, systemIds = None):
        self.currentDate = config.timeConfig['startDate']
        self.playerController = PlayerController(self)
        self.systems = []
        if systemIds is not None:
            for systemId in systemIds:
                self.systems.append(System(self, systemId))
        else:
            for _ in range(config.systemConfig['numSystems']):
                self.systems.append(System(self))
        self.scheduleLeagues()
        
    def timeTravel(self, days):
        for i in range(days):
            print(i)
            self.resolveQuotidia()
            self.advanceOneDay()
    
    def resolveQuotidia(self):
        self.playFixtures(self.currentDate)

    def playFixtures(self, date):
        for system in self.systems:
            for league in system.leagues:
                league.playOutstandingFixtures(date)
    
    def advanceOneDay(self):
        self.currentDate += datetime.timedelta(days = 1)
        self.playerController.advance()
    
    def scheduleLeagues(self):
        for system in self.systems:
            for league in system.leagues:
                Scheduler.scheduleLeagueFixtures(self.currentDate.year, league)
    
    def getClubByName(self, clubName):
        for system in self.systems:
            for club in system.clubs:
                if club.name == clubName:
                    return club
    
    def getFixtureById(self, fixtureId):
        for system in self.systems:
            for league in system.leagues:
                for fixture in league.fixtures:
                    if fixture.id == int(fixtureId):
                        return fixture

_instance = None

def Universe(systemIds = None):
    global _instance
    if _instance is None:
        _instance = _Universe(systemIds)
    return _instance