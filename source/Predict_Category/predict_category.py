import sys
import numpy as np
from objects import categoryModel
from constants import PARENT_DIR_PATH
sys.path.append(PARENT_DIR_PATH)
from config.config_details import cnn_params
from Train_Model.data_utils import get_data_vector, cnn_score_to_prob, probability_to_confidence_score

cat_model = categoryModel()


def predict_category_tree(product_name):
    """This function predicts category tree for the given product name using the 
    ensamble of multiple algorithms. Preference is  given to CNN. If confidence 
    score of CNN is lower than a threshold, output is given based on average 
    output probabilities of CNN and Naive Bayes algorithm.

    """
    first_level_cnn, second_level_cnn, fl_scores_cnn, fl_confidence_score_cnn = predict_category_tree_using_cnn(
        product_name)
    if fl_confidence_score_cnn >= cnn_params['confidence_threshold']:
        return first_level_cnn, second_level_cnn, fl_confidence_score_cnn
    first_level_nb, second_level_nb, fl_prob_nb, fl_confidence_score_nb = predict_category_tree_using_nb(
        product_name.lower())
    fl_prob_cnn = cnn_score_to_prob(fl_scores_cnn)
    fl_prob_avg = {}
    max_prob = 0
    best_category = ""
    for cat, prob in fl_prob_cnn.items():
        fl_prob_avg[cat] = (prob + fl_prob_nb[cat]) / 2.0
        if fl_prob_avg[cat] > max_prob:
            max_prob = fl_prob_avg[cat]
            best_category = cat
    first_level = best_category
    second_level = ""
    if first_level == first_level_cnn:
        second_level = second_level_cnn
    elif first_level == first_level_nb:
        second_level = second_level_nb
    else:
        second_level = predict_subcategory_using_cnn(product_name, first_level)
    first_level_confidence_score = probability_to_confidence_score(fl_prob_avg.values())
    return first_level, second_level, first_level_confidence_score


# Product name should be passed after converting to lowercase
def predict_category_tree_using_nb(l_product_name):
    vectorizer = cat_model.vectorizer
    clf_bayes = cat_model.clf_bayes
    clf_chi = cat_model.clf_chi
    clf_fp = cat_model.clf_fp

    second_level_vectorizer = cat_model.second_level_vectorizer
    second_level_clf_bayes = cat_model.second_level_clf_bayes
    second_level_clf_fpr = cat_model.second_level_clf_fpr

    class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
    class1_prob_vector = clf_bayes.predict_proba(
        vectorizer.transform([l_product_name]))[0]
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

    prob_vector = []
    if class3 == "Uncategorized":
        if class2 == "Uncategorized":
            prob_vector = class1_prob_vector
        else:
            prob_vector = class2_prob_vector
    else:
        prob_vector = class3_prob_vector
    first_level_prob = {cat: prob_vector[i] for i, cat in enumerate(clf_bayes.classes_)}
    first_level_confidence_score = probability_to_confidence_score(prob_vector)
    second_level = ""

    if first_level in cat_model.second_level_cat_names_set:
        prob_vector = second_level_clf_fpr[first_level].predict_proba(
            second_level_vectorizer[first_level].transform([l_product_name]))[0]
        if len(np.unique(prob_vector)) == 1:
            second_level = second_level_clf_bayes[first_level].predict(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
        else:
            second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]

    return first_level, second_level, first_level_prob, first_level_confidence_score


def predict_category_tree_using_cnn(product_name):
    """Predict Category tree for given product title using CNN. Output 
    second_level will be empty string if not applicable. Output 
    first_level_scores is a dictionary of scores corresponding to each label.

    """
    first_level = ""
    second_level = ""
    vocab_data = cat_model.clf_cnn_vocab_data
    x = get_data_vector(product_name, vocab_data['vocabulary_x'], vocab_data['sequence_length'])
    y_rand = np.zeros((1, len(vocab_data['vocabulary_inv_y'])))
    y_rand[0][0] = 1
    with cat_model.clf_cnn_sess.as_default():
        cnn = cat_model.clf_cnn
        feed_dict = {
            cnn.input_x: x,
            cnn.input_y: y_rand,
            cnn.dropout_keep_prob: 1.0
        }
        scores, pred = cat_model.clf_cnn_sess.run([cnn.scores, cnn.predictions], feed_dict)
        first_level = vocab_data['vocabulary_inv_y'][pred]
        scores = scores[0]
        first_level_scores = {category: scores[i]
                              for i, category in enumerate(vocab_data['vocabulary_inv_y'])}
        exp_scores = [2**score for score in scores]
        first_level_confidence_score = max(exp_scores) / sum(exp_scores)
    second_level = predict_subcategory_using_cnn(product_name, first_level)

    return first_level, second_level, first_level_scores, first_level_confidence_score


def predict_subcategory_using_cnn(product_name, first_level, default_second_level=""):
    """Given the product name and first level category name, this function 
    returns the second level sub-category predicted using CNN. If first_level 
    category is not among the categories for which second level category exist, 
    it returns default_second_level.

    """
    second_level = default_second_level
    if first_level in cat_model.second_level_cat_names_set:
        with cat_model.second_level_clf_cnn_sess[first_level].as_default():
            vocab_data = cat_model.second_level_clf_cnn_vocab_data[first_level]
            x = get_data_vector(product_name, vocab_data[
                                'vocabulary_x'], vocab_data['sequence_length'])
            y_rand = np.zeros((1, len(vocab_data['vocabulary_inv_y'])))
            y_rand[0][0] = 1
            cnn = cat_model.second_level_clf_cnn[first_level]
            feed_dict = {
                cnn.input_x: x,
                cnn.input_y: y_rand,
                cnn.dropout_keep_prob: 1.0
            }
            pred = cat_model.second_level_clf_cnn_sess[
                first_level].run([cnn.predictions], feed_dict)
            second_level = vocab_data['vocabulary_inv_y'][pred[0]]
    return second_level
