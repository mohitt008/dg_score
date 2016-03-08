import numpy as np
import os
from objects import categoryModel

cat_model = categoryModel()


# Product name should be passed after converting to lowercase
def predict_category_tree (l_product_name):
    #print "pid:", os.getpid()
    vectorizer = cat_model.vectorizer
    clf_bayes = cat_model.clf_bayes
    clf_chi = cat_model.clf_chi
    clf_fp = cat_model.clf_fp

    second_level_vectorizer = cat_model.second_level_vectorizer
    second_level_clf_bayes = cat_model.second_level_clf_bayes
    second_level_clf_fpr = cat_model.second_level_clf_fpr

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

    if class3 == "Uncategorized":
        if class1 == class2:
            first_level = class1
        elif class1 == "Uncategorized":
            first_level = class2
        elif class2 == "Uncategorized":
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

    return l_product_name, first_level, second_level

