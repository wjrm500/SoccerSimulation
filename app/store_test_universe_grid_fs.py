from models.Database import Database
from bson.binary import Binary
import gridfs
import sys

db = Database.getInstance()
cnx = db.cnx.grid_file
fs = gridfs.GridFS(cnx)

universeFilename = 'universe_' + sys.argv[1]
f = open(universeFilename, 'rb')
universe = f.read()
print('Saving {}'.format(universeFilename))
fs.put(universe, filename = universeFilename)