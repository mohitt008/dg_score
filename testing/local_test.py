__author__ = 'delhivery'
import sys
import os.path
import numpy as np
import re
import csv
import warnings
warnings.filterwarnings("ignore")

PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname('__file__')))
sys.path.append(PARENT_DIR+"/../source/")

from config.config_details import ROOT_PATH
from Predict_Category.objects import categoryModel
from Predict_Category.constants import CLEAN_PRODUCT_NAME_REGEX
from Train_Model.train import ngrams
cat_model = categoryModel()

vectorizer = cat_model.vectorizer
clf_bayes = cat_model.clf_bayes
clf_chi = cat_model.clf_chi
clf_fp = cat_model.clf_fp

second_level_vectorizer = cat_model.second_level_vectorizer
second_level_clf_bayes = cat_model.second_level_clf_bayes
second_level_clf_fpr = cat_model.second_level_clf_fpr



def single_output(product_name):

    l_product_name = product_name.lower()
    ngram_list=ngrams(l_product_name,1,1)
    clean_product_name = " ".join(ngram_list)
    l_product_name = clean_product_name

    class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
    class2_prob_vector = clf_chi.predict_proba(vectorizer.transform([l_product_name]))[0]
    class3_prob_vector = clf_fp.predict_proba(vectorizer.transform([l_product_name]))[0]

    if len(np.unique(class3_prob_vector)) == 1:
        class3 = "Uncategorized"
    else:
        class3 = clf_bayes.classes_[np.argmax(class3_prob_vector)]

    if len(np.unique(class2_prob_vector)) == 1:
        class2 = "Uncategorized"
    else:
        class2 = clf_bayes.classes_[np.argmax(class2_prob_vector)]

    return {'clean_product_name':clean_product_name,
            'class1':class1,
            'class2':class2,
            'class3':class3}


def test_first_level(products):
    f=open("/home/delhivery/newcatresults_4.csv",'w')
    writer=csv.writer(f)
    writer.writerow(['Name','Clean_Name','Orig','Cat1','Cat2','Cat3','Cat4'])
    #product_name,new_cat,new_subcat

    found_1,correct_1=0,0
    found_2,correct_2=0,0
    found_3,correct_3=0,0


    for i,product_desc in enumerate(products):
        print i
        product_name=product_desc.get('product_name')
        output_dict=single_output(product_name)
        cat= product_desc.get('new_cat')
        class1=output_dict.get('class1')
        class2=output_dict.get('class2')
        class3=output_dict.get('class3')
        clean_product_name=output_dict.get('clean_product_name')


        if class1!="Uncategorized":
            found_1+=1
            if class1==cat and cat!='Unclear' and cat!="Uncategorized":
                correct_1+=1

        if class2!="Uncategorized":
            found_2+=1
            if class2==cat and cat!='Unclear' and cat!="Uncategorized":
                correct_2+=1

        if class3!="Uncategorized":
            found_3+=1
            if class3==cat and cat!='Unclear' and cat!="Uncategorized":

                correct_3+=1

        writer.writerow([product_name,clean_product_name,cat,class1,class2,class3])

    print found_1,correct_1
    print found_2,correct_2
    print found_3,correct_3

    f.close()

def predict_category_test(product_name, cat_model):
    try:
        l_product_name = product_name.lower()
        product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
        clean_product_name = " ".join(product_words)
        print clean_product_name


        vectorizer = cat_model.vectorizer
        clf_bayes = cat_model.clf_bayes
        clf_chi = cat_model.clf_chi
        clf_rf = cat_model.clf_rf

        second_level_vectorizer = cat_model.second_level_vectorizer
        second_level_clf_bayes = cat_model.second_level_clf_bayes
        second_level_clf_fpr = cat_model.second_level_clf_fpr
        second_level_clf_rf = cat_model.second_level_clf_rf

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

        if first_level in cat_model.second_level_cat_names_set_nb:
            prob_vector = second_level_clf_fpr[first_level].predict_proba(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
            if len(np.unique(prob_vector)) == 1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]

        elif first_level in cat_model.second_level_cat_names_set_rf:
            prob_vector = second_level_clf_rf[first_level].predict_proba(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
            if len(np.unique(prob_vector)) == 1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]

        result = {}
        result['cat'] = class1,class2,class3
        result['scat'] = second_level
        return result

    except Exception as err:
        pass



if __name__=="__main__":

    # reader = csv.DictReader(open("/home/delhivery/catalognew/cataloguing/data/test_data_11feb.csv"))
    # output_file=open("/home/delhivery/dg2febresults.csv",'w')
    # writer = csv.writer(output_file)
    # for row in reader:
    #     product_name=row.get('product_name',"")
    #
    #     results = predict_category_test(product_name.encode('ascii','ignore'),cat_model)
    #     writer.writerow([product_name,results.get('cat'),results.get('scat')])
    # output_file.close()
    product_list=[]
    reader = csv.DictReader(open("/home/delhivery/catalognew/cataloguing/data/test_data_16feb.csv"))
    for row in reader:
        product_list.append(row)
    test_first_level(product_list[:10000])

    #test single item
    # print single_output("beauty item")

    # product_name,new_cat,new_subcat




