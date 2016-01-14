import redis
import raven
import sys
import ConfigParser
import os
from importlib import import_module
from pydisque.client import Client

# Add base path to import path
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         os.path.pardir))
sys.path.append(BASE_PATH)

# SK: Get environment from environment variable. 'local' if not present
env = os.getenv('ENVIRONMENT', 'local')
# SK: Load intended module as config
config = import_module('config.%s' % env)

# Queue config
config_parser = ConfigParser.RawConfigParser()
config_parser.read(BASE_PATH + '/config/queues.conf')
catfight_input = config_parser.get("Queues", "input_queue")
catfight_output = config_parser.get("Queues", "output_queue")

# Sentry
sentry_client = raven.Client(
    dsn = config.SENTRY_DSN
)

# Redis
redis_config = {
    'host': config.REDIS_IP,
    'port': 6379,
    'db'  : 0,
}
r = redis.Redis(**redis_config)
if not r.ping():
    sentry_client.captureException(
        message = "settings.py:: Failed to connect to redis",
        extra = {"error" : 'ping failed'})
    print "settings.py: Failed to connect to redis"
    sys.exit()

# Disque
client = Client([config.DISQUE_IP])
try:
    client.connect()
except Exception as disque_err:
    sentry_client.captureException(message = "settings.py: Failed to connect to disque",
                                   extra={"error" : disque_err})
    print "settings.py: Failed to connect to disque. error = ", disque_err
    sys.exit()

