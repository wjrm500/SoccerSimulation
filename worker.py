import os
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

ON_HEROKU = 'ON_HEROKU' in os.environ
if ON_HEROKU:
    conn = redis.from_url(os.environ.get('REDIS_URL'))
else:
    conn = redis.Redis()

if __name__ == '__main__':
    with Connection(conn):
        if not ON_HEROKU and os.name == 'nt':
            from rq_win import WindowsWorker
            worker = WindowsWorker(map(Queue, listen))
        else:
            worker = Worker(map(Queue, listen))
        worker.work()