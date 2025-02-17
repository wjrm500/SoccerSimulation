import sys

import gridfs
from models.Database import Database

db = Database.getInstance()
cnx = db.cnx.grid_file
fs = gridfs.GridFS(cnx)

universeFilename = "universe_" + sys.argv[1]
f = open(universeFilename, "rb")
universe = f.read()
print(f"Saving {universeFilename}")
fs.put(universe, filename=universeFilename)
