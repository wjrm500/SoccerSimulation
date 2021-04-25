from models.Database import Database
from bson.binary import Binary
import gridfs

### Passing formatted string to MongoClient class causes authentication error for some reason

db = Database.getInstance()
cnx = db.cnx.grid_file
fs = gridfs.GridFS(cnx)

f = open('universe_dvfwjndaes', 'rb')
universe = f.read()

fs.put(universe, filename = 'universe_dvfwjndaes')