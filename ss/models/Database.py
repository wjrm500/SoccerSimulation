from pymongo import MongoClient
import gridfs
import pickle
import os
from dotenv import load_dotenv
import gridfs

class Database:
    __instance__ = None

    def __init__(self):
        if Database.__instance__ is None:
            Database.__instance__ = self
            self.connect()
        else:
            raise Exception("You cannot create another Database class")
    
    def getUniverse(self, universeKey):
        if not hasattr(self, 'universe'):
            collection = self.cnx['soccersim']['universes']
            result = collection.find_one({'_id': universeKey})
            self.universe = result['value']
        return self.universe
    
    def getUniverseGridFile(self, universeKey):
        if not hasattr(self, 'universe'):
            fs = gridfs.GridFS(self.cnx.grid_file)
            result = fs.find_one({'filename': 'universe_' + universeKey})
            self.universe = result.read()
        return self.universe

    @staticmethod
    def getInstance():
        if not Database.__instance__:
            Database()
        return Database.__instance__
    
    def connect(self):
        load_dotenv()
        url = 'mongodb+srv://{user}:{pwd}@cluster0.tfn03.mongodb.net/{db}?retryWrites=true&w=majority'.format(
            user = os.environ.get('MONGO_USER'),
            pwd = os.environ.get('MONGO_PWD'),
            db = os.environ.get('MONGO_DB')
        )
        self.cnx = MongoClient(url)