import sys
import csv
from sklearn.externals import joblib
from constants import PARENT_DIR_PATH

sys.path.append(PARENT_DIR_PATH)

from config.config_details import second_level_cat_names, ROOT_PATH


class categoryModel(object):
    def __init__(self):
        self.second_level_cat_names_set = set(second_level_cat_names)
        self.vectorizer = joblib.load(ROOT_PATH + '/'+ 'data/Models/vectorizer.pkl')
        self.clf_bayes = joblib.load(ROOT_PATH + '/' + 'data/Models/clf_bayes.pkl')
        self.clf_chi = joblib.load(ROOT_PATH + '/' + 'data/Models/clf_chi.pkl')
        self.clf_fp = joblib.load(ROOT_PATH + '/' + 'data/Models/clf_fp.pkl')

        self.second_level_vectorizer = {}
        self.second_level_clf_bayes = {}
        self.second_level_clf_fpr = {}
        self.second_level_clf_rf = {}
        for cat_name in self.second_level_cat_names_set:
            self.second_level_vectorizer[cat_name] = joblib.load(ROOT_PATH + '/' +
                                                            'data/Models/SubModels/Vectorizer_' + cat_name)
            self.second_level_clf_bayes[cat_name] = joblib.load(ROOT_PATH + '/' +
                                                        'data/Models/SubModels/clf_bayes_' + cat_name)
            if cat_name in self.second_level_cat_names_set:
                self.second_level_clf_fpr[cat_name] = joblib.load(ROOT_PATH + '/' +
                                                        'data/Models/SubModels/clf_fpr_' + cat_name)
class dangerousModel(object):
    def __init__(self):
        file_dg_csv = open(ROOT_PATH + '/' + "data/DG_keywords.csv")
        reader = csv.reader(file_dg_csv)
        # Skip keys
        reader.next()
        self.dg_keywords = []
        for row in reader:
            tmp = []
            tmp.append(row[0].lower()) #store dangerous/ Non dangerous
            tmp.append(row[1].lower()) #store keyword
            tmp.append(row[2].lower()) #store CONTAIN list
            tmp.append(row[3].lower()) #store CONTAIN category
            tmp.append(row[4].lower()) #store EXCEPT list
            tmp.append(row[5].lower()) #store EXCEPT category
            tup = tuple(tmp)
            self.dg_keywords.append(tup)
        file_dg_csv.close()

