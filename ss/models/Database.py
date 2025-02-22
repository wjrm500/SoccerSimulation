import gridfs
from pymongo import MongoClient


class Database:
    __instance__ = None

    def __init__(self):
        if Database.__instance__ is None:
            Database.__instance__ = self
            self.connect()
        else:
            raise Exception("You cannot create another Database class")

    def universe_key_exists(self, universe_key):
        fs = gridfs.GridFS(self.cnx.grid_file)
        result = fs.find_one({"filename": universe_key})
        return bool(result)

    def get_universe_grid_file(self, universe_key):
        fs = gridfs.GridFS(self.cnx.grid_file)
        result = fs.find_one({"filename": universe_key})
        if result:
            return result.read()

    @staticmethod
    def get_instance():
        if not Database.__instance__:
            Database()
        return Database.__instance__

    def connect(self):
        url = "mongodb://mongodb:27017/soccersim"
        self.cnx = MongoClient(url, connect=False)
