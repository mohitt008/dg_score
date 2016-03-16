import sys
import csv
from sklearn.externals import joblib
from constants import PARENT_DIR_PATH, MODELS_PATH, \
        SUB_MODELS_PATH, DG_KEYWORDS_FILE

sys.path.append(PARENT_DIR_PATH)

from config.config_details import second_level_cat_names


class categoryModel(object):
    def __init__(self):
        self.second_level_cat_names_set = set(second_level_cat_names)

        self.vectorizer = joblib.load(MODELS_PATH + 'vectorizer.pkl',
                                      mmap_mode = 'r')
        self.clf_bayes = joblib.load(MODELS_PATH + 'clf_bayes.pkl',
                                     mmap_mode = 'r')
        self.clf_chi = joblib.load(MODELS_PATH + 'clf_chi.pkl',
                                   mmap_mode = 'r')
        self.clf_fp = joblib.load(MODELS_PATH + 'clf_fp.pkl',
                                  mmap_mode = 'r')

        self.second_level_vectorizer = {}
        self.second_level_clf_bayes = {}
        self.second_level_clf_fpr = {}
        self.second_level_clf_rf = {}

        for cat_name in self.second_level_cat_names_set:
            self.second_level_vectorizer[cat_name] = joblib.load(
                SUB_MODELS_PATH + '/Vectorizer_' + cat_name, mmap_mode = 'r')

            self.second_level_clf_bayes[cat_name] = joblib.load(
                SUB_MODELS_PATH + '/clf_bayes_' + cat_name, mmap_mode = 'r')

            if cat_name in self.second_level_cat_names_set:
                self.second_level_clf_fpr[cat_name] = joblib.load(
                    SUB_MODELS_PATH + '/clf_fpr_' + cat_name, mmap_mode = 'r')


class dangerousModel(object):
    def __init__(self):
        file_dg_csv = open(DG_KEYWORDS_FILE)
        reader = csv.reader(file_dg_csv)
        # Skip keys
        reader.next()
        self.dg_keywords = []
        for row in reader:
            tmp = []
            # dangerous/ Non dangerous
            tmp.append(row[0].lower())
            # keyword
            tmp.append(row[1].lower())
            # CONTAIN list
            tmp.append(row[2].lower())
            # CONTAIN category
            tmp.append(row[3].lower())
            # EXCEPT list
            tmp.append(row[4].lower())
            # EXCEPT category
            tmp.append(row[5].lower())

            tup = tuple(tmp)
            self.dg_keywords.append(tup)
        file_dg_csv.close()
