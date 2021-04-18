from config import systemConfig
from League import League
from Database import Database

class System:
    def __init__(self, universe, systemId = None):
        self.universe = universe
        self.leagues = []
        if systemId is not None:
            db = Database.getInstance()
            systemData = db.cnx['soccersim']['systems'].find_one({
                '_id': systemId
            })
        else:
            ### TODO: Get random untaken system
            pass
        self.id = systemData['_id']
        self.name = systemData['system_name']
        for _ in range(systemConfig['numLeaguesPerSystem']):
            self.leagues.append(League(self))