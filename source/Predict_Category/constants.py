import os
import re
import sys

# GET Parent path
PARENT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.path.pardir))
sys.path.append(PARENT_DIR_PATH)

from config.config_details import ROOT_PATH

VOLUME_ML_REGEX = re.compile('[0-9]+[\s]*ml')

# Alpha-num. Remove all punctuation, spaces etc
ALPHA_NUM_REGEX = re.compile('[\W_]+')

# Redis cache expiry 7 days (in sec)
CACHE_EXPIRY = 604800

# logging file path
LOGGING_PATH = '/var/log/cat_subcat_logs/cat_subcat.log'


# CAT Disque Path
CATFIGHT_LOGGING_PATH = '/var/log/cat_subcat_logs/cat_subcat_disque.log'

# Models path
MODELS_PATH = ROOT_PATH + '/data/Models/'
SUB_MODELS_PATH = ROOT_PATH + '/data/Models/SubModels'

# DG KEYwords FILE PATH
DG_KEYWORDS_FILE = ROOT_PATH + "/data/DG_keywords.csv"

# Celery Logging path
CELERY_LOGGING_PATH = '/var/log/cat_subcat_logs/celery.log'

LOG_DB_NAME = 'logs'

# Assume 1ms maximum mongo server selection delay
MAX_SEV_SEL_DELAY = 1

REPLICA_SET = 'rs0'

CATFIGHT_COLLECTION = 'catfight'

CELERY_QUEUE = "catfight_tasks"
