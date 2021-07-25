from models.Database import Database
from bson.binary import Binary
import sys

db = Database.getInstance()
collection = db.cnx['soccersim']['universes']
print('Opening file universe_' + sys.argv[1])
f = open('universe_' + sys.argv[1], 'rb')
universe = f.read()
collection.insert_one({
    '_id': sys.argv[1],
    'value': universe
})