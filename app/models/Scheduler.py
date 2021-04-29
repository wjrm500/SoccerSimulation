from datetime import date, timedelta
import random
from Fixture import Fixture
import copy

class Scheduler:
    fixturesCreated = 0

    @classmethod
    def scheduleFixture(cls, date, gameweek, tournament, clubX, clubY):
        if not hasattr(tournament, 'fixtures'):
            tournament.fixtures = []
        cls.fixturesCreated += 1
        fixture = Fixture(copy.copy(cls.fixturesCreated), tournament, date, clubX, clubY)
        fixture.setGameweek(gameweek)
        tournament.fixtures.append(fixture)

    @classmethod
    def scheduleLeagueFixtures(cls, year, league, weekday = 5):
        schedule = cls.roundRobinScheduler(league, robinType = 'double')
        currentDate = date(year, 1, 1)
        gameweek = 1
        while True:
            if currentDate.year > year or not schedule.get(gameweek): ### Exit loop when year changes / when fixtures have been exhausted
                return
            if currentDate.weekday() == weekday:
                for game in schedule[gameweek]:
                    clubX, clubY = game['home'], game['away']
                    cls.scheduleFixture(currentDate, gameweek, league, clubX, clubY)
                gameweek += 1
            currentDate += timedelta(days = 1) 
    
    @classmethod
    def roundRobinScheduler(cls, tournament, robinType = 'single', returnedObject = 'dict'):
        numClubs = len(tournament.clubs)
        if numClubs % 2 != 0:
            raise Exception('Number of clubs must be even')
        schedule = []
        fixturesPerWeek = int(numClubs / 2)
        maxIndex = fixturesPerWeek - 1
        for i in range(numClubs - 1):
            newGameweek = {}
            if i == 0:
                clubsForPopping = copy.copy(tournament.clubs)
                for j in range(fixturesPerWeek):
                    newGameweek[j] = [clubsForPopping.pop(0), clubsForPopping.pop()]
            else:
                lastGameweek = schedule[i - 1]
                for j in range(fixturesPerWeek):
                    if j == 0:
                        clubOne = tournament.clubs[0]
                    elif j == 1:
                        clubOne = lastGameweek[0][1]
                    else:
                        clubOne = lastGameweek[j - 1][0]

                    if j != maxIndex:
                        clubTwo = lastGameweek[j + 1][1]
                    else:
                        clubTwo = lastGameweek[maxIndex][0]
                    
                    newGameweek[j] = [clubOne, clubTwo]
            schedule.append(newGameweek)
        
        for i, gameweek in enumerate(schedule):
            if i % 2 != 0: ### If index is odd - to only flip teams on alternate gameweeks
                for key, value in gameweek.items():
                    gameweek[key] = [value[1], value[0]] ### Flip home and away teams
        
        if robinType == 'double': ### If double round-robin
            flippedSchedule = [copy.copy(gameweek) for gameweek in schedule] ### copy.copy(schedule) does not work because the list objects containing clubs in schedule are mutated // copy.deepcopy(schedule) does not work because club objects are duplicated so effectively a separate set of clubs is referenced in second half of schedule
            for i, gameweek in enumerate(flippedSchedule):
                for key, value in gameweek.items():
                    gameweek[key] = [value[1], value[0]] ### Flip home and away teams
            schedule = schedule + flippedSchedule

        reformattedSchedule = {}
        for i, gameweek in enumerate(schedule):
            if returnedObject == 'dict':
                fixtureList = [{'home': value[0], 'away': value[1]} for value in gameweek.values()]
            elif returnedObject == 'fixture':
                fixtureList = [Fixture(tournament, clubX = value[0], clubY = value[1]) for value in gameweek.values()]
            reformattedSchedule[i + 1] = fixtureList

        return reformattedSchedule