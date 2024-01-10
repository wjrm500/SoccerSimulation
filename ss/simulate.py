from .models.Universe import Universe
from .models.Database import Database
import gridfs
import redis
from .send_email import send_email
import ss.utils as utils
import time

r = redis.Redis(host='redis', port=6379)

def simulate(customConfig, systemId, universeKey):
    ### Create Universe, taking in input parameters from user
    universe = Universe(customConfig = customConfig, systemIds = [systemId])
    universe.universeKey = universeKey
    daysToTimeTravel = 300
    universe.timeTravel(daysToTimeTravel, r)
    pickledUniverse = utils.joblibDumps(universe)
    db = Database.getInstance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickledUniverse, filename = universeKey)
    if r.exists('email_' + universeKey):
        while not Database.getInstance().universeKeyExists(universeKey):
            time.sleep(5)
        recipient_address = r.get('email_' + universeKey).decode('utf-8')
        send_email(recipient_address, universeKey)
    r.flushall()