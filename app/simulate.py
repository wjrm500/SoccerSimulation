import sys
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app\\models")
from Universe import Universe
import random
import string
from Database import Database
import gridfs
import sys
import pickle

def simulate(customConfig, systemId):
    ### Create Universe, taking in input parameters from user
    universe = Universe(customConfig = customConfig, systemIds = [systemId])
    universe.timeTravel(350)
    pickledUniverse = pickle.dumps(universe)
    letters = string.ascii_lowercase
    universeKey = ''.join(random.choice(letters) for i in range(10))
    universeFilename = 'universe_' + universeKey
    db = Database.getInstance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickledUniverse, filename = universeFilename)
    return universeKey