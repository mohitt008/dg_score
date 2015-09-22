import re
from constants import ALPHA_NUM_REGEX, CACHE_EXPIRY, \
        CLEAN_PRODUCT_NAME_REGEX, VOLUME_ML_REGEX
from settings import r
import json
import numpy as np
import copy

# SK: TODO: Integrate new dang logic and breakdown into functions
def predict_category(product_name, cat_model, dang_model):
    l_product_name = product_name.lower()
    product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
    clean_product_name = " ".join(product_words)
    
    vectorizer = cat_model.vectorizer
    clf_bayes = cat_model.clf_bayes
    clf_chi = cat_model.clf_chi
    clf_rf = cat_model.clf_rf

    second_level_vectorizer = cat_model.second_level_vectorizer
    second_level_clf_bayes = cat_model.second_level_clf_bayes
    second_level_clf_fpr = cat_model.second_level_clf_fpr

    class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
    class2_prob_vector = clf_chi.predict_proba(vectorizer.transform([l_product_name]))[0]
    class3_prob_vector = clf_rf.predict_proba(vectorizer.transform([l_product_name]))[0]

    if len(np.unique(class2_prob_vector)) == 1:
        class2 = "Delhivery_Others"
    else:
        class2 = clf_bayes.classes_[np.argmax(class2_prob_vector)]
    if len(np.unique(class3_prob_vector)) == 1:
        class3 = "Delhivery_Others"
    else:
        class3 = clf_bayes.classes_[np.argmax(class3_prob_vector)]

    if class3 == "Delhivery_Others":
        if class1 == class2:
            first_level = class1
        elif class1 == "Delhivery_Others":
            first_level = class2
        elif class2 == "Delhivery_Others":
            first_level = class1
        else:
            first_level = class2
    else:
        first_level = class3

    second_level = ""

    if first_level in cat_model.second_level_cat_names_set:
        prob_vector = second_level_clf_fpr[first_level].predict_proba(
            second_level_vectorizer[first_level].transform([l_product_name]))[0]
        if len(np.unique(prob_vector)) == 1:
            second_level = second_level_clf_bayes[first_level].predict(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
        else:
            second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]

    for word in dang_model.non_dangerous_set:
        if word in clean_product_name:
            clean_product_name = clean_product_name.replace(word, " ")

    dangerous_flag = False
    for word in dang_model.dangerous_word_set:
        if word in clean_product_name:
            dangerous_flag = True
            break

    if not dangerous_flag and first_level in dang_model.dangerous_cat_set:
        for word in dang_model.dangerous_ambi_set:
            if word in clean_product_name:
                dangerous_flag = True
                break
    
    # TODO: false positives in kitchenware etc ...
    if not dangerous_flag and re.search(VOLUME_ML_REGEX, clean_product_name):
        dangerous_flag = True

    result = {}
    result['category'] = first_level
    result['sub_category'] = second_level
    result['dangerous'] = dangerous_flag
    return result

# SK: TODO: Use log ?
def process_product(product_name_dict, disque, cat_model, dang_model, log):
    results = {}
    results_cache = ''
    
    product_name = product_name_dict.get('prd', "")
    if product_name:
        if disque:
            final_result = {}
            original_dict = copy.deepcopy(product_name_dict)

        product_name_clean = (re.sub(ALPHA_NUM_REGEX, '', product_name)).lower()
        product_name_key = 'catfight:' +':' + product_name_clean
        results_cache = r.get(product_name_key)
        if not results_cache:
            results = predict_category(product_name.encode('ascii','ignore'),
                                       cat_model, dang_model)
            if results:
                r.setex(product_name_key, json.dumps(results), CACHE_EXPIRY)
                results['cached'] = False
        else:
            results = json.loads(results_cache)
            results['cached'] = True
    else:
        results['invalid_product_name'] = True
    
    if disque:
        final_result = original_dict
        final_result['result'] = results
        return final_result
    else:
        results['waybill'] = product_name_dict.get('wbn', None)
        return results

