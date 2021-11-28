from pymongo import MongoClient
import gridfs
import pickle
import os
from dotenv import load_dotenv
import gridfs

class Database:
    __instance__ = None

    def __init__(self):
        self.universes = {}
        if Database.__instance__ is None:
            Database.__instance__ = self
            self.connect()
        else:
            raise Exception("You cannot create another Database class")
    
    def universeKeyExists(self, universeKey):
        fs = gridfs.GridFS(self.cnx.grid_file)
        result = fs.find_one({'filename': universeKey})
        return bool(result)
    
    def getUniverseGridFile(self, universeKey):
        fs = gridfs.GridFS(self.cnx.grid_file)
        result = fs.find_one({'filename': universeKey})
        if result:
            self.universes[universeKey] = result.read()
            return self.universes[universeKey]

    @staticmethod
    def getInstance():
        if not Database.__instance__:
            Database()
        return Database.__instance__
    
    def connect(self):
        load_dotenv()
        url = 'mongodb+srv://{user}:{pwd}@cluster0.tfn03.mongodb.net/{db}?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE'.format(
            user = os.environ.get('MONGO_USER'),
            pwd = os.environ.get('MONGO_PWD'),
            db = os.environ.get('MONGO_DB')
        )
        self.cnx = MongoClient(url, connect = False)