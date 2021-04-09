from config import systemConfig
from League import League

class System:
    def __init__(self, universe):
        self.universe = universe
        self.leagues = []
        for _ in range(systemConfig['numLeaguesPerSystem']):
            self.leagues.append(League(self))