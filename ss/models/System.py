from ..config import systemConfig
from .Database import Database
from .League import League


class System:
    def __init__(self, universe, systemId=None):
        self.universe = universe
        self.leagues = []
        if systemId is not None:
            db = Database.getInstance()
            systemData = db.cnx["soccersim"]["systems"].find_one({"_id": systemId})
        else:
            ### TODO: Get random untaken system
            pass
        self.id = systemData["_id"]
        self.name = systemData["system_name"]
        numLeaguesPerSystem = (
            universe.config["numLeaguesPerSystem"] or systemConfig["numLeaguesPerSystem"]
        )
        for _ in range(numLeaguesPerSystem):
            self.leagues.append(League(self))
