import os
import sys
import numpy as np
import logging
import json
import traceback

from flask import Flask, request,Response
from sklearn.externals import joblib
#from config_details import second_level_cat_names
from logging.handlers import RotatingFileHandler

#from Train_Model.train import ngrams
PARENT_DIR_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(PARENT_DIR_PATH)

second_level_cat_names=\
            ["Beauty Products and Personal Care",
                  "Camera and Photos",
                  "Mobile Phone, Tablets and Accesories",
                  "Apparel & Accessories",
                  "Watches, Eyewear and Jewellery",
                  "Electronics and Appliances",
                  "Home and Kitchen",
                  "Computers and Laptops",
                  "Shoes and Footwear"
                 ]


second_level_cat_names_set=set(second_level_cat_names)

#logging file path
LOGGING_PATH='/var/log/cat_subcat_logs/cat_subcat.log'

app = Flask(__name__)
handler = RotatingFileHandler(LOGGING_PATH,maxBytes=10000000,backupCount=5)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.logger.info("Loading Process Started")
vectorizer=joblib.load(PARENT_DIR_PATH+'/Models/vectorizer.pkl')
clf_bayes=joblib.load(PARENT_DIR_PATH+'/Models/clf_bayes.pkl')
clf_chi=joblib.load(PARENT_DIR_PATH+'/Models/clf_chi.pkl')
clf_fpr=joblib.load(PARENT_DIR_PATH+'/Models/clf_fpr.pkl')

second_level_vectorizer={}
second_level_clf_bayes={}
second_level_clf_fpr={}
for cat_name in second_level_cat_names_set:
    second_level_vectorizer[cat_name]=joblib.load(PARENT_DIR_PATH+'/Models/SubModels/Vectorizer_'+cat_name)
    second_level_clf_bayes[cat_name]=joblib.load(PARENT_DIR_PATH+'/Models/SubModels/clf_bayes_'+cat_name)
    second_level_clf_fpr[cat_name]=joblib.load(PARENT_DIR_PATH+'/Models/SubModels/clf_fpr_'+cat_name)

app.logger.info("Loading Process Complete")

def predict_category(product_name):
    app.logger.info("Request received {}".format(str(product_name)))

    try:
        l_product_name = product_name.lower()
        class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
        class2_prob_vector = clf_chi.predict_proba(vectorizer.transform([l_product_name]))[0]
        class3_prob_vector = clf_fpr.predict_proba(vectorizer.transform([l_product_name]))[0]

        if len(np.unique(class2_prob_vector))==1:
            class2 = "NA"
        else:
            class2 = clf_bayes.classes_[np.argmax(class2_prob_vector)]
        if len(np.unique(class3_prob_vector))==1:
            class3 = "NA"
        else:
            class3 = clf_bayes.classes_[np.argmax(class2_prob_vector)]

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
            if len(np.unique(prob_vector))==1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]


        # prob_vector= second_level_clf[class_name].predict_proba(
            #second_level_vectorizer[class_name].transform([product_name.lower()]))[0]

        app.logger.info("Result produced {} --> {}".format(
            str(first_level), str(second_level)))
    except Exception as err:
        app.logger.error(
            'Traceback: {}'.format(traceback.format_exc()))
        app.logger.error(
            'Exec Info: {}'.format(sys.exc_info())[0])
        app.logger.error(
            'Exception {} occurred against product: {}'.format(
                err, product_name))

    return (first_level,second_level)

@app.route('/get_category', methods = ['POST'])
def get_category():
    try:
        list_product_names = list(request.get_json())
        output_list=[]
        app.logger.info("Request Received {}".format (str(list_product_names)))

        for product_name in list_product_names:
            result = dict()
            result['category'], result['sub_category'] = predict_category(product_name)
            output_list.append(result)

        return Response(json.dumps(output_list),  mimetype='application/json')
    except Exception as err:
        app.logger.error(
            'Exception {} occurred against payload: {}'.format(
                err, list_product_names))


if __name__=='__main__':
    app.run(port=8000)

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
