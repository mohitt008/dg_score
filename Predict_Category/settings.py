import redis
import raven
import sys
from pydisque.client import Client

## For sentry settings
sentry_client = raven.Client(
    #dsn = 'https://f65cb67d524443d2b8f9f53d3da0b3fd:5c6cb4e0d70d41efa9f77a585ade3dad@app.getsentry.com/48657'
    dsn = 'https://12bc0e7f582c48069090c5c876b923cf:7e13376d29fd4e81a5b585380729537b@app.getsentry.com/51526'
)

## for redis configuration
config = {
    #'host': 'd1-redis-addfix.iqi3ba.ng.0001.apse1.cache.amazonaws.com',
    'host': 'localhost',
    'port':6379,
    'db':0,
}

try:
    r = redis.Redis(**config)
except Exception as redis_err:
    sentry_client.captureException(
        message = "settings.py:: Failed to connect to redis",
        extra = {"error":redis_err})
    sys.exit()

## for disque connection
client = Client(["127.0.0.1:7711", "127.0.0.1:7712", "127.0.0.1:7713"])

try:
    client.connect()
except Exception as disque_err:
    sentry_client.captureException(message = "settings.py:Failed to connect to disque",
                                   extra={"error" : disque_err})
    sys.exit()


RESULTS_URL = {'express': 'http://localhost/done-services/output'}

disque_output_queue = "disque_catfight_output_queue"
disque_input_queue = "disque_catfight_input_queue"

