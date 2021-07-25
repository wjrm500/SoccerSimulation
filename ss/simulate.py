from .models.Universe import Universe
import random
import string
from .models.Database import Database
import gridfs
import pickle

def simulate(customConfig, systemId, r):
    ### Create Universe, taking in input parameters from user
    universe = Universe(customConfig = customConfig, systemIds = [systemId])
    daysToTimeTravel = ((customConfig['numClubsPerLeague'] - 1) * 2 * 7) + 7
    print(daysToTimeTravel)
    universe.timeTravel(daysToTimeTravel, r)
    pickledUniverse = pickle.dumps(universe)
    letters = string.ascii_lowercase
    universeKey = ''.join(random.choice(letters) for i in range(10))
    universeFilename = 'universe_' + universeKey
    db = Database.getInstance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickledUniverse, filename = universeFilename)
    return universeKey