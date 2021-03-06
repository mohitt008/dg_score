import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import sys
from copy import deepcopy

# from multiprocessing import Pool, cpu_count
# from functools import partial

from constants import CATFIGHT_LOGGING_PATH, CELERY_QUEUE
from find_categories import process_product
from settings import client, sentry_client, catfight_input, catfight_output
from objects import dangerousModel
from tasks import add_result_to_mongo

logger = logging.getLogger('Catfight App')
handler = RotatingFileHandler(CATFIGHT_LOGGING_PATH, maxBytes=200000000,
                              backupCount=5)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Loading Process Started")

try:
    dang_model = dangerousModel()
except Exception as err:
    logger.error("Error {} while loading models".format(err))
    sentry_client.captureException(
        message = "service_category_disque : Failed to load models",
        extra = {"error" : err})
    print "service_cat_disque: Failed to load dg model...exiting"
    sys.exit()

logger.info("Loading Process Complete")


def validate_product_args(record):
    value = True
    error_response = {}
    if type(record) is not dict:
        error_response['type'] = 'MissingDict'
        value = False
    else:
        if not record.get('prd', None):
            error_response = {'prd': 'MissingProductName'}
            value = False
    return value, error_response


def get_category(list_product_names, job_id, username):
    output_list = []
    dg_report = {}
    logger.info("Request received {0} for username {1}".format(
        list_product_names, username))
    if list_product_names:
        for product_name_dict in list_product_names:
            try:
                valid_record, error_response = validate_product_args(
                    product_name_dict)
                if valid_record:
                    result, dg_report = process_product(product_name_dict,
                                             dang_model,
                                             logger,
                                             username)
                    timestamp = datetime.now()
                    output_list.append(result)
                else:
                    if type(product_name_dict) is dict:
                        for key, value in product_name_dict.items():
                            error_response[key] = value
                            error_response["error"] = "BAD REQUEST"
                    timestamp = datetime.now()
                    result = error_response
                    output_list.append(error_response)
                add_result_to_mongo.apply_async(
                    (username, result, timestamp, dg_report),
                    queue = CELERY_QUEUE)
            except Exception as err:
                timestamp = datetime.now()
                result = {}
                result = deepcopy(product_name_dict)
                result['error'] = err
                add_result_to_mongo.delay(username, result, timestamp, dg_report)
                logger.error(
                    'get_category:Exception {} occurred against input: {} \
                    for job_id {} for username {}'.
                    format(err, list_product_names, job_id, username))
                sentry_client.captureException(
                    message = "Exception occurred in get_category",
                    extra = {"error" : err, "job_id" : job_id,
                             "product_name_dict" : product_name_dict,
                             "username" : username
                             })
                pass
    else:
        error_response = {'error' : 'MissingProductList'}
        output_list.append(error_response)

    logger.info("Result produced {} for username {}".format(
        output_list, username))

    return output_list


def add_results_to_disque(results, vendor, username, job_id):
    """
    Callback function for catfight results.
    Adds results alongwith vendor and username to output disque.
    """
    if results:
        results_dict = {}
        results_dict['vendor'] = str(vendor)
        results_dict['username'] = str(username)
        results_dict['catfight_results'] = results
        second_job_id = client.add_job(catfight_output,
                                       json.dumps(results_dict),
                                       retry = 5)
        logger.info("Successfully added to queue catfight_output \
                    with Job ID {}".format(second_job_id))
    else:
        logger.info(
            "No results found for Job ID {} with job {}".format(job_id))


def get_products():
    """
    Function to fetch job from disque queue, catfight_input, splitting the job
    into vendor and results, and calling get_category to generate products
    details for the job passed
    """

    # SK: Disabled multiprocessing as it doesn't work properly with tf
    # p = Pool(processes=cpu_count())
    while True:
        try:
            jobs = client.get_job([catfight_input])
            for queue_name, job_id, job in jobs:
                logger.info("Successfully fetched from queue catfight_input \
                            GET Job ID {} with job {}".
                            format(job_id, job))
                job_data = json.loads(job)
                username = job_data['username']
                products = json.loads(job_data['payload'])

                """
                custom_callback = partial(add_results_to_disque,
                                          vendor = job_data['vendor'],
                                          username = username,
                                          job_id = job_id)
                p.apply_async(get_category,
                              args = (products, job_id, username,),
                              callback = custom_callback)
                """
                res = get_category(products, job_id, username)
                add_results_to_disque(res, job_data['vendor'],
                                      username, job_id)
                client.ack_job(job_id)

        except Exception as e:
            logger.error(
                "get_products failed for Job ID {} with job {} with error {}".
                format(job_id, job, e))
            sentry_client.captureException(
                message = "get_products failed",
                extra = {"error" : e})
            pass

if __name__=='__main__':
    get_products()
