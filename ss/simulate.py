from .models.Universe import Universe
import random
import string
from .models.Database import Database
import gridfs
import pickle
import os
import redis

ON_HEROKU = 'ON_HEROKU' in os.environ
if ON_HEROKU:
    r = redis.from_url(os.environ.get('REDIS_URL'))
else:
    r = redis.Redis()

def simulate(customConfig, systemId):
    r.set('simulation_progress', 0);
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