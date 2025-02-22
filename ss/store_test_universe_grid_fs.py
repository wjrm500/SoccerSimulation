import sys

import gridfs
from models.Database import Database

db = Database.get_instance()
cnx = db.cnx.grid_file
fs = gridfs.GridFS(cnx)

universe_filename = "universe_" + sys.argv[1]
f = open(universe_filename, "rb")
universe = f.read()
print(f"Saving {universe_filename}")
fs.put(universe, filename=universe_filename)
