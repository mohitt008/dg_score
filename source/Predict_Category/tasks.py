import logging
from celery import Celery
from celery.utils.log import get_task_logger

from constants import CATFIGHT_COLLECTION, CELERY_LOGGING_PATH
from settings import sentry_client, log_db, redis_url


# TODO: logger doesn't work
celery = Celery('tasks', broker=redis_url, CELERY_ACKS_LATE=True)
logger = get_task_logger('CeleryTasks')
handler = logging.handlers.RotatingFileHandler(CELERY_LOGGING_PATH, maxBytes=2000000,
                                               backupCount=5)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@celery.task
def add_result_to_mongo(username, result, timestamp, dg_report):
    if not result:
        sentry_client.captureException(
            message='tasks.py: add_log_to_mongo: Empty Result'
        )
        return None

    mongo_collection = username + '_' + CATFIGHT_COLLECTION
    try:
        if result.get('wbn', None):
            wbn = result.pop('wbn')
            logger.info('Received wbn {}'.format(wbn))
            result['date'] = timestamp.strftime('%Y-%m-%d')
            result['time'] = timestamp.strftime('%H:%M:%S,%f')
            result['dg_check'] = dg_report
            mongo_update = log_db[mongo_collection].update(
                {'_id': wbn}, result, upsert=True)
        else:
            # VV: What if we need to capture an event which is not an exception
            sentry_client.captureException(
                message='tasks.py: add_log_to_mongo: Missing wbn for result {}'.format(
                    result)
            )
            logger.info('No wbn received for result {}'.format(result))

    except Exception as mongo_err:
        sentry_client.captureException(
            message='tasks.py: add_log_to_mongo: Mongo Error {} for result {}'.format(
                mongo_err, result)
        )
        logger.error(
            'Error occurred for result {} with wbn {}'.format(result, wbn))
