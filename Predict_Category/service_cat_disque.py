import os
import sys
import numpy as np
import logging
import json
import traceback
import csv
import re

from constants import second_level_cat_names, CLEAN_PRODUCT_NAME_REGEX, \
        VOLUME_ML_REGEX, ALPHA_NUM_REGEX, CACHE_EXPIRY, CATFIGHT_LOGGING_PATH

from settings import r, sentry_client

from flask import Flask, request,Response
from sklearn.externals import joblib
from logging.handlers import RotatingFileHandler


logger = logging.getLogger('Addfix App')
handler = RotatingFileHandler(CATFIGHT_LOGGING_PATH,maxBytes=1000000000,backupCount=20)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Loading Process Started")

vectorizer = joblib.load(PARENT_DIR_PATH + '/Models/vectorizer.pkl')
clf_bayes = joblib.load(PARENT_DIR_PATH + '/Models/clf_bayes.pkl')
clf_chi = joblib.load(PARENT_DIR_PATH + '/Models/clf_chi.pkl')
clf_rf = joblib.load(PARENT_DIR_PATH + '/Models/clf_l1_rf.pkl')

second_level_vectorizer = {}
second_level_clf_bayes = {}
second_level_clf_fpr = {}
for cat_name in second_level_cat_names_set:
    second_level_vectorizer[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                    '/Models/SubModels/Vectorizer_' + cat_name)
    second_level_clf_bayes[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                   '/Models/SubModels/clf_bayes_' + cat_name)
    second_level_clf_fpr[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                 '/Models/SubModels/clf_fpr_' + cat_name)

app.logger.info("Loading Process Complete")

def validate_product_args(record):
    value = True
    error_response = {}
    if not record.get('product_name', None):
        error_response = {'error': ERROR_CODE['MissingProductName']}
        value = False
    if not record.get('wbn', None):
        error_response = {'error': ERROR_CODE['MissingWBN']}
        value = False
    return value, error_response

def get_category(list_product_names, job_id):
    try:
        output_list = []
        app.logger.info("Request received {}".format(list_product_names))
        if list_product_names:
            for product_name_dict in list_product_names:
                valid_record, error_response = validate_product_args(product_name_dict)
                if valid_record:
                    result = find_localities(product_name_dict,True,model,logger)
                    output_list.append(result)
                else:
                    for key, value in product_name_dict.items():
                        error_response[key] = value
                        output_list.append(error_response)
        app.logger.info("Result produced {}".format(output_list))

    except Exception as err:
        app.logger.error(
            'Exception {} occurred against payload: {}'.format(
                err, list_product_names))

        sentry_client.captureException(
            message = "predict.py: Exception occured",
            extra = {"error" : err, "payload" : list_product_names})

def get_products():
    """
    Function to fetch job from disque queue, catfight_input, splitting the job
    into vendor and results, and calling search_addresses to generate products
    for the job passed 
    """
    while True:
        try:
            jobs = client.get_job(['catfight_input'])
            for queue_name, job_id, job in jobs:
                job_data = json.loads(job)
                vendor = job_data['vendor']
                products = json.loads(job_data['products'])

                logger.info("Request received for vendor {}".format(vendor))
                results = get_category(products,job_id)
                if results:
                    second_job_id = client.add_job('catfight_output', str(vendor) + '@' +json.dumps(results),retry = 5)
                    client.ack_job(job_id)
                    logger.info("Successfully fetched from Disque queue catfight_input GET Job ID {} with job {}".format(job_id,job))
                    logger.info("Successfully added to Disque queue catfight_output with Job ID {} and job {}".format(job_id,job))
                else:
                    logger.info("No results found for Job ID {} with job {}".format(job_id,job))
        except Exception as e:
            logger.info("Function get_products failed for Job ID {} with job {} with error {}".format(job_id,job,e))
            sentry_client.captureException(
                message = "get_products failed", 
                extra = {"error":e})
            pass

if __name__=='__main__':
    get_products()