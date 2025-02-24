import redis
from rq import Queue

from ss.models.Database import Database
from worker import conn

# Initialise global services
db = Database.get_instance()  # MongoDB
q = Queue(connection=conn)
r = redis.Redis(host="redis", port=6379)
TTL_SECONDS = 3600  # store simulation data for one hour
