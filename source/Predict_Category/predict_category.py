import sys
import json
import numpy as np
import tensorflow as tf
from objects import categoryModel
from constants import MODELS_PATH, SUB_MODELS_PATH, PARENT_DIR_PATH
sys.path.append(PARENT_DIR_PATH)
from config.config_details import cnn_params
from Train_Model.data_utils import get_data_vector
from Train_Model.text_cnn import TextCNN

cat_model = categoryModel()


# Product name should be passed after converting to lowercase
def predict_category_tree(l_product_name):
    first_level, second_level, fl_scores, fl_confidence_score = predict_category_tree_using_cnn(
        l_product_name)
    if fl_confidence_score >= cnn_params['confidence_threshold']:
        return first_level, second_level
    vectorizer = cat_model.vectorizer
    clf_bayes = cat_model.clf_bayes
    clf_chi = cat_model.clf_chi
    clf_fp = cat_model.clf_fp

    second_level_vectorizer = cat_model.second_level_vectorizer
    second_level_clf_bayes = cat_model.second_level_clf_bayes
    second_level_clf_fpr = cat_model.second_level_clf_fpr

    class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
    class2_prob_vector = clf_chi.predict_proba(
        vectorizer.transform([l_product_name]))[0]
    class3_prob_vector = clf_fp.predict_proba(
        vectorizer.transform([l_product_name]))[0]

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

    return first_level, second_level


def predict_category_tree_using_cnn(l_product_name):
    """Predict Category tree for given product title using CNN. Output 
    second_level will be empty string if not applicable. Output 
    first_level_scores is a dictionary of scores corresponding to each label.

    """
    first_level = ""
    second_level = ""
    vocab_data = json.load(open(MODELS_PATH + "clf_cnn_vocab.txt"))
    x = get_data_vector(l_product_name, vocab_data['vocabulary_x'], vocab_data['sequence_length'])
    y_rand = np.zeros((1, len(vocab_data['vocabulary_inv_y'])))
    y_rand[0][0] = 1
    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=cnn_params['allow_soft_placement'],
            log_device_placement=cnn_params['log_device_placement'])
        sess = tf.Session(config=session_conf)
        with sess.as_default():
            cnn = TextCNN(
                sequence_length=x.shape[1],
                num_classes=len(vocab_data['vocabulary_inv_y']),
                vocab_size=len(vocab_data['vocabulary_x']),
                embedding_size=cnn_params['embedding_dim'],
                filter_sizes=cnn_params['filter_sizes'],
                num_filters=cnn_params['num_filters'],
                l2_reg_lambda=cnn_params['l2_reg_lambda'])
            saver = tf.train.Saver()
            saver.restore(sess, MODELS_PATH + "clf_cnn.ckpt")
            feed_dict = {
                cnn.input_x: x,
                cnn.input_y: y_rand,
                cnn.dropout_keep_prob: 1.0
            }
            scores, pred = sess.run([cnn.scores, cnn.predictions], feed_dict)
            first_level = vocab_data['vocabulary_inv_y'][pred]
            scores = scores[0]
            first_level_scores = {category: scores[i]
                                  for i, category in enumerate(vocab_data['vocabulary_inv_y'])}
            first_level_confidence_score = max(scores) / sum(scores)
    if first_level in cat_model.second_level_cat_names_set:
        with tf.Graph().as_default():
            session_conf = tf.ConfigProto(
                allow_soft_placement=cnn_params['allow_soft_placement'],
                log_device_placement=cnn_params['log_device_placement'])
            sess = tf.Session(config=session_conf)
            with sess.as_default():
                vocab_data = json.load(open(SUB_MODELS_PATH + "/clf_cnn_" +
                                            first_level.replace(' ', '_') + "_vocab.txt"))
                x = get_data_vector(l_product_name, vocab_data[
                                    'vocabulary_x'], vocab_data['sequence_length'])
                y_rand = np.zeros((1, len(vocab_data['vocabulary_inv_y'])))
                y_rand[0][0] = 1
                cnn = TextCNN(
                    sequence_length=x.shape[1],
                    num_classes=len(vocab_data['vocabulary_inv_y']),
                    vocab_size=len(vocab_data['vocabulary_x']),
                    embedding_size=cnn_params['embedding_dim'],
                    filter_sizes=cnn_params['filter_sizes'],
                    num_filters=cnn_params['num_filters'],
                    l2_reg_lambda=cnn_params['l2_reg_lambda'])
                saver = tf.train.Saver()
                saver.restore(sess, SUB_MODELS_PATH + "/clf_cnn_" + first_level.replace(' ', '_'))
                feed_dict = {
                    cnn.input_x: x,
                    cnn.input_y: y_rand,
                    cnn.dropout_keep_prob: 1.0
                }
                pred = sess.run([cnn.predictions], feed_dict)
                second_level = vocab_data['vocabulary_inv_y'][pred[0]]
    return first_level, second_level, first_level_scores, first_level_confidence_score
