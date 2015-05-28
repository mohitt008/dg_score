import os, sys
import numpy as np
import flask


PARENT_DIR_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(PARENT_DIR_PATH)
from Train_Model.train import ngrams
from sklearn.externals import joblib
from config_details import second_level_cat_names
second_level_cat_names_set=set(second_level_cat_names)

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


def predict_category(product_name):
    # print ngrams(product_name)
    class1 = clf_bayes.predict(vectorizer.transform([product_name.lower()]))[0]
    class2_prob_vector = clf_chi.predict_proba(vectorizer.transform([product_name.lower()]))[0]
    class3_prob_vector = clf_fpr.predict_proba(vectorizer.transform([product_name.lower()]))[0]

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
        prob_vector = second_level_clf_fpr[first_level].predict_proba(second_level_vectorizer[first_level].transform([product_name.lower()]))[0]
        if len(np.unique(prob_vector))==1:
            second_level = second_level_clf_bayes[first_level].predict(second_level_vectorizer[first_level].transform([product_name.lower()]))[0]
        else:
            second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]



        # prob_vector= second_level_clf[class_name].predict_proba(second_level_vectorizer[class_name].transform([product_name.lower()]))[0]
    return (first_level,second_level)




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