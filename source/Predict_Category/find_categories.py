import re
from constants import ALPHA_NUM_REGEX, CACHE_EXPIRY, CLEAN_PRODUCT_NAME_REGEX
from settings import r, sentry_client
import json
import copy
from check_dg import predict_dangerous
from predict_category import predict_category_tree

def get_category_dg(product_name, wbn, cat_model, dang_model, logger, username):
    try:
        l_product_name = product_name.lower()

        first_level, second_level = predict_category_tree(l_product_name, cat_model)

        product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
        clean_product_name = " ".join(product_words)

        dg_report = predict_dangerous(clean_product_name, wbn, first_level,
                                      dang_model.dg_keywords, logger, username)

        result = {}
        result['cat'] = first_level
        result['scat'] = second_level
        result['dg'] = dg_report['dangerous']
        return result

    except Exception as err:
        logger.error(
            'Exception {} occurred against product: {}'.format(
                err, product_name))
        sentry_client.captureException(
            message = "predict.py: Exception occured",
            extra = {"error" : err, "product_name" : product_name})

def process_product(product_name_dict, cat_model, dang_model, logger, username):
    results = {}
    results_cache = ''

    product_name = product_name_dict.get('prd', "")
    if product_name:
        final_result = {}
        original_dict = copy.deepcopy(product_name_dict)

        product_name_clean = (re.sub(ALPHA_NUM_REGEX, '', product_name)).lower()
        product_name_key = 'catfight:' +':' + product_name_clean
        results_cache = r.get(product_name_key)
        wbn = product_name_dict.get('wbn', "")
        if not results_cache:
            results = get_category_dg(product_name.encode('ascii','ignore'),
                                      wbn, cat_model, dang_model,
                                      logger, username)
            if results:
                r.setex(product_name_key, json.dumps(results), CACHE_EXPIRY)
                results['cached'] = False
        else:
            results = json.loads(results_cache)
            l_product_name = product_name.lower()
            product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
            clean_product_name = " ".join(product_words)
            first_level = results['cat']
            dg_report = predict_dangerous(clean_product_name, wbn, first_level,
                                      dang_model.dg_keywords, logger, username)

            results['dg'] = dg_report['dangerous']
            results['cached'] = True
    else:
        results['invalid_product_name'] = True

    final_result = original_dict
    if not results:
        #SK: Don't send empty result or bad format.
        #SK: Default dg = true(ops verified)
        results['cat'] = "Not Found"
        results['scat'] = "Not Found"
        results['dg'] = True
    final_result['result'] = results
    return final_result

