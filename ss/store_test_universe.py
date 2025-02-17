import sys

from models.Database import Database

db = Database.getInstance()
collection = db.cnx["soccersim"]["universes"]
print("Opening file universe_" + sys.argv[1])
f = open("universe_" + sys.argv[1], "rb")
universe = f.read()
collection.insert_one({"_id": sys.argv[1], "value": universe})
