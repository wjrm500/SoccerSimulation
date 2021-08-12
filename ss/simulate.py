from .models.Universe import Universe
from .models.Database import Database
import gridfs
import pickle
import os
import redis
from .send_email import send_email
import ss.utils as utils

ON_HEROKU = 'ON_HEROKU' in os.environ
if ON_HEROKU:
    r = redis.from_url(os.environ.get('REDIS_URL'))
else:
    r = redis.Redis()

def simulate(customConfig, systemId, universeKey):
    ### Create Universe, taking in input parameters from user
    universe = Universe(customConfig = customConfig, systemIds = [systemId])
    universe.universeKey = universeKey
    daysToTimeTravel = 300
    print(daysToTimeTravel)
    universe.timeTravel(daysToTimeTravel, r)
    if r.exists('email_' + universeKey):
        recipient_address = r.get('email_' + universeKey).decode('utf-8')
        send_email(recipient_address, universeKey)
    pickledUniverse = utils.joblibDumps(universe)
    db = Database.getInstance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickledUniverse, filename = universeKey)
    r.flushdb()