
import re
from constants import ALPHA_NUM_REGEX, CACHE_EXPIRY
from settings import r, sentry_client
import json
import copy
from predict_category import predict_category_tree

from dg_predictor import DGPredictor


def predict_dg(product_name, category, logger, wbn = None):
    category = category.lower()
    predictor = DGPredictor(
        product_name,
        category,
        logger
    )
    report = predictor.predict(wbn)
    return report


def get_category_dg(product_name, wbn, dang_model, logger, username):
    try:
        l_product_name = product_name.lower()

        first_level, second_level, first_level_confidence_score = \
                predict_category_tree(l_product_name)
        if not first_level:
            first_level = 'Uncategorized'
        if not second_level:
            second_level = ''

        dg_report = predict_dg(
            l_product_name,
            first_level,
            logger,
            wbn
        )

        result = {}
        result['cat'] = first_level
        result['scat'] = second_level
        result['cat_confidence'] = first_level_confidence_score
        result['dg'] = dg_report['dangerous']
        result['prohibited'] = dg_report.get('prohibited', False)
        return result

    except Exception as err:
        logger.error(
            'Exception {} occurred against product: {}'.format(
                err, product_name))
        sentry_client.captureException(
            message="predict.py: Exception occured",
            extra={"error": err, "product_name": product_name})


def process_product(product_name_dict, dang_model, logger, username):
    results = {}
    results_cache = ''

    product_name = product_name_dict.get('prd', "")
    if product_name:
        final_result = {}
        original_dict = copy.deepcopy(product_name_dict)

        product_name_clean = re.sub(ALPHA_NUM_REGEX, '', product_name)
        product_name_clean = product_name_clean.lower()
        product_name_key = 'catfight:' + ':' + product_name_clean
        results_cache = r.get(product_name_key)
        wbn = product_name_dict.get('wbn', "")
        if not results_cache:
            results = get_category_dg(product_name.encode('ascii', 'ignore'),
                                      wbn, dang_model, logger, username)
            if results:
                r.setex(product_name_key, json.dumps(results), CACHE_EXPIRY)
                results['cached'] = False
        else:
            results = json.loads(results_cache)
            l_product_name = product_name.lower()
            first_level = results['cat']

            dg_report = predict_dg(
                l_product_name,
                first_level,
                logger,
                wbn
            )

            results['dg'] = dg_report['dangerous']
            results['prohibited'] = dg_report.get('prohibited', False)
            results['cached'] = True
    else:
        results['invalid_product_name'] = True

    final_result = original_dict
    if not results:
        # SK: Don't send empty result or bad format.
        # SK: Default dg = true(ops verified)
        results['cat'] = "Not Found"
        results['scat'] = "Not Found"
        results['dg'] = True
        results['prohibited'] = False
    final_result['result'] = results
    return final_result

