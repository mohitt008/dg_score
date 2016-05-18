import sys
import csv
import json
import tensorflow as tf
from sklearn.externals import joblib
from constants import PARENT_DIR_PATH, MODELS_PATH, \
    SUB_MODELS_PATH, DG_KEYWORDS_FILE

sys.path.append(PARENT_DIR_PATH)

from Train_Model.text_cnn import TextCNN
from config.config_details import second_level_cat_names, cnn_params


class categoryModel(object):

    def __init__(self):
        vocab_data = json.load(open(MODELS_PATH + "clf_cnn_vocab.txt"))
        with tf.Graph().as_default():
            session_conf = tf.ConfigProto(
                allow_soft_placement=cnn_params['allow_soft_placement'],
                log_device_placement=cnn_params['log_device_placement'])
            sess = tf.Session(config=session_conf)
            with sess.as_default():
                cnn = TextCNN(
                    sequence_length=vocab_data['sequence_length'],
                    num_classes=len(vocab_data['vocabulary_inv_y']),
                    vocab_size=len(vocab_data['vocabulary_x']),
                    embedding_size=cnn_params['embedding_dim'],
                    filter_sizes=cnn_params['filter_sizes'],
                    num_filters=cnn_params['num_filters'],
                    l2_reg_lambda=cnn_params['l2_reg_lambda'])
                saver = tf.train.Saver()
                saver.restore(sess, MODELS_PATH + "clf_cnn.ckpt")
                self.clf_cnn = cnn
                self.clf_cnn_sess = sess
                self.clf_cnn_vocab_data = vocab_data

        self.second_level_cat_names_set = set(second_level_cat_names)

        self.second_level_clf_cnn = {}
        self.second_level_clf_cnn_sess = {}
        self.second_level_clf_cnn_vocab_data = {}

        for cat_name in self.second_level_cat_names_set:
            vocab_data = json.load(open(SUB_MODELS_PATH + "/clf_cnn_" +
                                        cat_name.replace(' ', '_') + \
                                        "_vocab.txt"))
            with tf.Graph().as_default():
                session_conf = tf.ConfigProto(
                    allow_soft_placement=cnn_params['allow_soft_placement'],
                    log_device_placement=cnn_params['log_device_placement'])
                sess = tf.Session(config=session_conf)
                with sess.as_default():
                    cnn = TextCNN(
                        sequence_length=vocab_data['sequence_length'],
                        num_classes=len(vocab_data['vocabulary_inv_y']),
                        vocab_size=len(vocab_data['vocabulary_x']),
                        embedding_size=cnn_params['embedding_dim'],
                        filter_sizes=cnn_params['filter_sizes'],
                        num_filters=cnn_params['num_filters'],
                        l2_reg_lambda=cnn_params['l2_reg_lambda'])
                    saver = tf.train.Saver()
                    saver.restore(sess, SUB_MODELS_PATH + "/clf_cnn_" + \
                                  cat_name.replace(' ', '_'))
                    self.second_level_clf_cnn[cat_name] = cnn
                    self.second_level_clf_cnn_sess[cat_name] = sess
                    self.second_level_clf_cnn_vocab_data[cat_name] = vocab_data
        # Important note: Since only CNN is being used to predict category tree,
        # we have commented line below as we don't need to load nb model. One
        # should uncomment the line below if he/she need to use any of the
        # predict_category_tree_using_ensamble or predict_category_tree_using_nb
        # function in predict_category.py file

        # self.load_nb_model()

    def load_nb_model(self):
        self.vectorizer = joblib.load(MODELS_PATH + 'vectorizer.pkl',
                                      mmap_mode='r')
        self.clf_bayes = joblib.load(MODELS_PATH + 'clf_bayes.pkl',
                                     mmap_mode='r')
        self.clf_chi = joblib.load(MODELS_PATH + 'clf_chi.pkl',
                                   mmap_mode='r')
        self.clf_fp = joblib.load(MODELS_PATH + 'clf_fp.pkl',
                                  mmap_mode='r')
        self.second_level_vectorizer = {}
        self.second_level_clf_bayes = {}
        self.second_level_clf_fpr = {}
        self.second_level_clf_rf = {}
        for cat_name in self.second_level_cat_names_set:
            self.second_level_vectorizer[cat_name] = joblib.load(
                SUB_MODELS_PATH + '/Vectorizer_' + cat_name, mmap_mode='r')

            self.second_level_clf_bayes[cat_name] = joblib.load(
                SUB_MODELS_PATH + '/clf_bayes_' + cat_name, mmap_mode='r')

            if cat_name in self.second_level_cat_names_set:
                self.second_level_clf_fpr[cat_name] = joblib.load(
                    SUB_MODELS_PATH + '/clf_fpr_' + cat_name, mmap_mode='r')

# DG detection logic
# https://docs.google.com/document/d/1dUEMZHwGC9WJxPlgNPNCiQzvIy5JyLvO_aui0d7tHMM/
class dangerousModel(object):

    def __init__(self):
        file_dg_csv = open(DG_KEYWORDS_FILE)
        reader = csv.reader(file_dg_csv)
        # Skip keys
        reader.next()
        self.dg_keywords = []
        # Dict with client name as key and list of words as value
        self.exact_names = {}

        # Dict with client name as key and result as value
        self.client_dict_default_value = {}

        for row in reader:
            tmp = []
            # dangerous / non dangerous
            default_val = row[0].lower()
            tmp.append(default_val)

            # client
            clients = row[1].lower()
            tmp.append(clients)

            # keyword
            keyword = row[2].lower()
            tmp.append(keyword)
            # CONTAIN list
            tmp.append(row[3].lower())
            # CONTAIN category
            tmp.append(row[4].lower())
            # EXCEPT list
            tmp.append(row[5].lower())
            # EXCEPT category
            tmp.append(row[6].lower())

            tup = tuple(tmp)

            if default_val == "3":
                if not clients:
                    # product names marked as dg
                    # irrespective of clients i.e empty client
                    key = "all_clients"
                else:
                    # SK: For value = 3, only 1 client should be present
                    key = clients

                val = []
                names = keyword.split(';')
                for name in names:
                    val.append(name.lower().strip())
                self.exact_names[key] = val

            elif (default_val == '0' or default_val == '1') and not keyword:
                # Clients which have a default value (dg or non dg)
                client_list = clients.split(';')
                for client in client_list:
                    self.client_dict_default_value[client] = default_val
            else:
                self.dg_keywords.append(tup)

        file_dg_csv.close()


    def get_exact_names(self):
        return self.exact_names


    def get_client_dict_default(self):
        return self.client_dict_default_value
