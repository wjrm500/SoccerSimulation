from .models.Universe import Universe
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

def simulate(customConfig, systemId, universeKey):
    r.set('simulation_progress', 0);
    ### Create Universe, taking in input parameters from user
    universe = Universe(customConfig = customConfig, systemIds = [systemId])
    daysToTimeTravel = ((customConfig['numClubsPerLeague'] - 1) * 2 * 7) + 7
    print(daysToTimeTravel)
    universe.timeTravel(daysToTimeTravel, r)
    pickledUniverse = pickle.dumps(universe)
    db = Database.getInstance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickledUniverse, filename = universeKey)