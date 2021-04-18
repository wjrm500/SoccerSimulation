from pymongo import MongoClient
import pickle

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

    @staticmethod
    def getInstance():
        if not Database.__instance__:
            Database()
        return Database.__instance__
    
    def connect(self):
        url = 'mongodb+srv://{user}:{pwd}@cluster0.tfn03.mongodb.net/{db}?retryWrites=true&w=majority'.format(
            user = os.environ.get('MONGO_USER'),
            pwd = os.environ.get('MONGO_PWD'),
            db = os.environ.get('MONGO_DB')
        )
        self.cnx = MongoClient(url)