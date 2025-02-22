from ..config import system_config
from .Database import Database
from .League import League


class System:
    def __init__(self, universe, system_id=None):
        self.universe = universe
        self.leagues = []
        if system_id is not None:
            db = Database.get_instance()
            system_data = db.cnx["soccersim"]["systems"].find_one({"_id": system_id})
        else:
            ### TODO: Get random untaken system
            pass
        self.id = system_data["_id"]
        self.name = system_data["system_name"]
        num_leagues_per_system = (
            universe.config["num_leagues_per_system"] or system_config["num_leagues_per_system"]
        )
        for _ in range(num_leagues_per_system):
            self.leagues.append(League(self))
