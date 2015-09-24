import sys
import csv
from sklearn.externals import joblib
from constants import PARENT_DIR_PATH, second_level_cat_names

sys.path.append(PARENT_DIR_PATH)

class categoryModel(object):
    def __init__(self):
        self.second_level_cat_names_set = set(second_level_cat_names)
        self.vectorizer = joblib.load(PARENT_DIR_PATH + '/Models/vectorizer.pkl')
        self.clf_bayes = joblib.load(PARENT_DIR_PATH + '/Models/clf_bayes.pkl')
        self.clf_chi = joblib.load(PARENT_DIR_PATH + '/Models/clf_chi.pkl')
        self.clf_rf = joblib.load(PARENT_DIR_PATH + '/Models/clf_l1_rf.pkl')

        self.second_level_vectorizer = {}
        self.second_level_clf_bayes = {}
        self.second_level_clf_fpr = {}
        for cat_name in self.second_level_cat_names_set:
            self.second_level_vectorizer[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                            '/Models/SubModels/Vectorizer_' + cat_name)
            self.second_level_clf_bayes[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                        '/Models/SubModels/clf_bayes_' + cat_name)
            self.second_level_clf_fpr[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                        '/Models/SubModels/clf_fpr_' + cat_name)

class dangerousModel(object):
    def __init__(self):
        self.dangerous_cat_set = set()
        f_dang = open(PARENT_DIR_PATH + "/dangerous_categories.csv")
        reader = csv.DictReader(f_dang)
        for row in reader:
            if row['dang'] == "1":
                self.dangerous_cat_set.add(row['cat_name'])
        f_dang.close()

        self.dangerous_word_set = set()
        f_dang = open(PARENT_DIR_PATH + "/dangerous_words.csv")
        reader = csv.reader(f_dang)
        for row in reader:
            self.dangerous_word_set.add(row[0])
        f_dang.close()

        self.dangerous_ambi_set = set()
        f_dang = open(PARENT_DIR_PATH + "/dangerous_ambi.csv")
        reader = csv.reader(f_dang)
        for row in reader:
            self.dangerous_ambi_set.add(row[0])
        f_dang.close()

        self.non_dangerous_set = set()
        f_dang = open(PARENT_DIR_PATH + "/non_dangerous_words.csv")
        reader = csv.reader(f_dang)
        for row in reader:
            self.non_dangerous_set.add(row[0])
        f_dang.close()

