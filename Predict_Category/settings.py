import redis
import raven
import sys

## For sentry settings
sentry_client = raven.Client(
    dsn = 'https://f65cb67d524443d2b8f9f53d3da0b3fd:5c6cb4e0d70d41efa9f77a585ade3dad@app.getsentry.com/48657'
)

## for redis configuration
config = {
    'host': 'd1-redis-addfix.iqi3ba.ng.0001.apse1.cache.amazonaws.com',
    'port':6379,
    'db':0,
}

try:
    r = redis.Redis(**config)
except Exception as redis_err:
    sentry_client.captureException(
        message = "Settings.py:: Failed to connect to redis",
        extra = {"error":redis_err})
    sys.exit()

