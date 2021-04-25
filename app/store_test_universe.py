from models.Database import Database
from bson.binary import Binary

### Passing formatted string to MongoClient class causes authentication error for some reason

db = Database.getInstance()
collection = db.cnx['soccersim']['universes']
f = open('universe_bellqprldx', 'rb')
universe = f.read()
collection.insert_one({
    '_id': 'bellqprldx',
    'value': universe
})