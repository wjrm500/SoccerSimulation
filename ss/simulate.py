from .models.Universe import Universe
from .models.Database import Database
import gridfs
import redis
from .send_email import send_email
import ss.utils as utils
import time

r = redis.Redis(host='redis', port=6379)

def simulate(customConfig, systemId, universeKey):
    # Create Universe based on the input parameters.
    universe = Universe(customConfig=customConfig, systemIds=[systemId])
    universe.universeKey = universeKey
    daysToTimeTravel = 300
    universe.timeTravel(daysToTimeTravel, r)
    
    # Serialise the Universe.
    pickledUniverse = utils.joblibDumps(universe)
    
    # Persist the serialised Universe into GridFS.
    db = Database.getInstance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickledUniverse, filename=universeKey)
    
    # If an email was provided, wait until the Universe is confirmed in GridFS then send an email.
    if r.exists("email_" + universeKey):
        while not Database.getInstance().universeKeyExists(universeKey):
            time.sleep(5)
        recipient_address = r.get("email_" + universeKey).decode("utf-8")
        send_email(recipient_address, universeKey)
    
    # Remove the data in the Redis cache no longer needed:
    r.delete("simulation_progress_" + universeKey)
    r.delete("email_" + universeKey)
