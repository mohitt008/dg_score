import os
import sys
import numpy as np
import logging
import json
import traceback
import csv
import re

from sklearn.externals import joblib

from constants import second_level_cat_names, CLEAN_PRODUCT_NAME_REGEX, \
        VOLUME_ML_REGEX, ALPHA_NUM_REGEX, CACHE_EXPIRY

from settings import r, sentry_client

from flask import Flask, request,Response
from logging.handlers import RotatingFileHandler

PARENT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(PARENT_DIR_PATH)

dangerous_cat_set = set()
f_dang = open(PARENT_DIR_PATH+"/dangerous_categories.csv")
reader = csv.DictReader(f_dang)
for row in reader:
    if row['dang'] == "1":
        dangerous_cat_set.add(row['cat_name'])
f_dang.close()

dangerous_word_set = set()
f_dang = open(PARENT_DIR_PATH + "/dangerous_words.csv")
reader = csv.reader(f_dang)
for row in reader:
    dangerous_word_set.add(row[0])
f_dang.close()

dangerous_ambi_set = set()
f_dang = open(PARENT_DIR_PATH + "/dangerous_ambi.csv")
reader = csv.reader(f_dang)
for row in reader:
    dangerous_ambi_set.add(row[0])
f_dang.close()

non_dangerous_set = set()
f_dang = open(PARENT_DIR_PATH + "/non_dangerous_words.csv")
reader = csv.reader(f_dang)
for row in reader:
    non_dangerous_set.add(row[0])
f_dang.close()

second_level_cat_names_set = set(second_level_cat_names)

#logging file path
LOGGING_PATH = '/var/log/cat_subcat_logs/cat_subcat.log'

app = Flask(__name__)
handler = RotatingFileHandler(LOGGING_PATH, maxBytes = 100000000, backupCount = 5)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.logger.info("Loading Process Started")
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

def predict_category(product_name):

    try:
        l_product_name = product_name.lower()
        product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
        clean_product_name = " ".join(product_words)
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

        if first_level in second_level_cat_names_set:
            prob_vector = second_level_clf_fpr[first_level].predict_proba(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
            if len(np.unique(prob_vector)) == 1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]

        for word in non_dangerous_set:
            if word in clean_product_name:
                clean_product_name = clean_product_name.replace(word, " ")

        dangerous_flag = False
        for word in dangerous_word_set:
            if word in clean_product_name:
                dangerous_flag = True
                break

        if not dangerous_flag and first_level in dangerous_cat_set:
            for word in dangerous_ambi_set:
                if word in clean_product_name:
                    dangerous_flag = True
                    break
        # TODO: false positives in kitchenware etc ...
        if not dangerous_flag and re.search(VOLUME_ML_REGEX, clean_product_name):
            dangerous_flag = True

        # prob_vector= second_level_clf[class_name].predict_proba(

        result = {}
        result['category'] = first_level
        result['sub_category'] = second_level
        result['dangerous'] = dangerous_flag
        return result

        #second_level_vectorizer[class_name].transform([product_name.lower()]))[0]

    except Exception as err:
        app.logger.error(
            'Traceback: {}'.format(traceback.format_exc()))
        app.logger.error(
            'Exec Info: {}'.format(sys.exc_info())[0])
        app.logger.error(
            'Exception {} occurred against product: {}'.format(
                err, product_name))
        sentry_client.captureException(
            message = "predict.py: Exception occured",
            extra = {"error" : err, "product_name" : product_name})

@app.route('/get_category', methods = ['POST'])
def get_category():
    try:
        list_product_names = list(request.get_json())
        output_list = []

        for product_name_dict in list_product_names:
            app.logger.info("Request received {}".format(product_name_dict))
            results = {}
            results_cache = ''
            
            product_name = product_name_dict.get('product_name', "")
            if product_name:
                product_name_clean = (re.sub(ALPHA_NUM_REGEX, '', product_name)).lower()
                product_name_key = 'catfight:' +':' + product_name_clean
                results_cache = r.get(product_name_key)
                if not results_cache:
                    results = predict_category(product_name.encode('ascii','ignore'))
                    if results:
                        r.setex(product_name_key, json.dumps(results), CACHE_EXPIRY)
                        results['cached'] = False
                else:
                    results = json.loads(results_cache)
                    results['cached'] = True
            else:
                results['invalid_product_name'] = True
            
            results['waybill'] = product_name_dict.get('wbn', None)
            
            app.logger.info("Result produced {}".format(results))
    
            output_list.append(results)

        return Response(json.dumps(output_list),  mimetype='application/json')
    
    except Exception as err:
        app.logger.error(
            'Exception {} occurred against payload: {}'.format(
                err, list_product_names))

        sentry_client.captureException(
            message = "predict.py: Exception occured",
            extra = {"error" : err, "payload" : list_product_names})

if __name__=='__main__':
    app.run()

"""
if __name__=='__main__':
    import csv
    f=open('/home/delhivery/Downloads/products_demo.csv')
    f2=open('/home/delhivery/Downloads/products_demo_results3.csv','w')
    reader=csv.reader(f)
    writer=csv.writer(f2)
    firstrow=True
    for row in reader:
        if firstrow:
            writer.writerow(['wbn','prod','cat','subcat'])
            firstrow = False
            continue
        if row[1]:
            first,second=predict_category(row[1])
            writer.writerow([row[0],row[1],first,second])
"""

