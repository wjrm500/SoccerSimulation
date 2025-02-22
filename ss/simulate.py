import time

import gridfs
import redis

import ss.utils as utils

from .email_service import EmailService
from .models.Database import Database
from .models.Universe import Universe

r = redis.Redis(host="redis", port=6379)


def simulate(custom_config, system_id, universe_key):
    # Create Universe based on the input parameters.
    universe = Universe(custom_config=custom_config, system_ids=[system_id])
    universe.universe_key = universe_key
    days_to_time_travel = 300
    universe.time_travel(days_to_time_travel, r)

    # Serialise the Universe.
    pickled_universe = utils.joblib_dumps(universe)

    # Persist the serialised Universe into GridFS.
    db = Database.get_instance()
    cnx = db.cnx.grid_file
    fs = gridfs.GridFS(cnx)
    fs.put(pickled_universe, filename=universe_key)

    # If an email was provided, wait until the Universe is confirmed in GridFS then send an email.
    if r.exists("email_" + universe_key):
        while not Database.get_instance().universe_key_exists(universe_key):
            time.sleep(5)
        recipient_address = r.get("email_" + universe_key).decode("utf-8")
        email_service = EmailService()
        email_service.send_simulation_complete_email(recipient_address, universe_key)

    # Remove the data in the Redis cache no longer needed:
    r.delete("simulation_progress_" + universe_key)
    r.delete("email_" + universe_key)
