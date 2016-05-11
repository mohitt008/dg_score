"""
This file contains useful data utility functions i.e. data read/write, data cleaning, 
feature extraction etc.
"""
import re
import os
import csv
import math
import itertools
import numpy as np
from collections import Counter

PADDING_WORD = "<PAD/>"
plural_dict = {}
ROOT_PATH = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                      os.path.pardir)), os.path.pardir))
if os.path.exists(ROOT_PATH + "/data/word_list_verified.csv"):
    with open(ROOT_PATH + "/data/word_list_verified.csv", 'rb') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 0 and row[2] != '0':
                plural_dict[row[0]] = row[1]
else:
    print "Plural Dictionary Built"
    print "Important Warning: File for Plural dictionary not found"


def get_plural_free_word(word):
    if word.endswith('s'):
        word = plural_dict.get(word, word)
    return word


def clean_str(input_string):
    """This function cleans out the characters other than alphabets, numerics and '.'. 
    Alphabet characters are further converted to lower case.

    """
    input_string = re.sub(r'\s*-\s*(?=[0-9]+\b)', '', input_string)
    input_string = re.sub(r"[^A-Za-z0-9.]", " ", input_string)
    return input_string.lower()


def read_data_and_labels(filename):
    """This function reads the csv file with path filename and returns first 
    column entries as x_text and 2nd column entries as y_text. Each entry of 
    x_text is again a list of words occurring in corresponding row and 1st 
    column

    """
    file = open(filename, 'rb')
    reader = csv.reader(file)
    x_text = []
    y_text = []
    for i, row in enumerate(reader):
        if i > 0 and row[1] != "Unclear":
            x_text.append(row[0])
            y_text.append(row[1])
    x_text = [clean_str(sentence) for sentence in x_text]
    x_text = [sentence.split() for sentence in x_text]
    x_text = [[get_plural_free_word(word) for word in sentence] for sentence in x_text]
    return [x_text, y_text]


def build_vocab(x_text, y_text):
    """Builds vocabulary of input words and category labels

    """
    # Vocabulary for input text data
    word_counts_x = Counter(itertools.chain(*x_text))
    vocabulary_inv_x = [x[0] for x in word_counts_x.most_common()]
    vocabulary_x = {x: i for i, x in enumerate(vocabulary_inv_x)}
    word_dist = [x[1] for x in word_counts_x.most_common()]
    # Vocabulary for labels
    word_counts_y = Counter(y_text)
    vocabulary_inv_y = [x[0] for x in word_counts_y.most_common()]
    vocabulary_y = {x: i for i, x in enumerate(vocabulary_inv_y)}
    label_dist = [x[1] for x in word_counts_y.most_common()]
    return [vocabulary_x, vocabulary_inv_x, vocabulary_y, vocabulary_inv_y, word_dist, label_dist]


def get_term_category_matrix(x_text, y_text, vocabulary_x, vocabulary_y, word_dist, min_word_count):
    """This function returns term category matrix. Rows of matrix represent 
    terms (input words) and columns of matrix represent category. 

    In the term category matrix we return here only those terms are considered 
    whose occurence in complete input data is more than min_word_count

    """
    num_valid_terms = len([count for count in word_dist if count >= min_word_count])
    tc_mat = np.zeros((num_valid_terms, len(vocabulary_y)), dtype=np.int)
    for i, sentence in enumerate(x_text):
        for word in sentence:
            if word_dist[vocabulary_x[word]] >= min_word_count:
                tc_mat[vocabulary_x[word]][vocabulary_y[y_text[i]]] += 1
    return tc_mat


def combine_feature_selection_scores(score_matrix, weights=None, combination_method="average"):
    """Rows of score_matrix represent terms and columns of score_matrix represent 
    categories and each entity of score_matrix represent score for the corresponding 
    term and category. This function aggregates the scores over categories (columns). 
    Size of output score_agg is same as the number of terms

    """
    num_rows = len(score_matrix)
    score_agg = np.zeros((num_rows))
    if combination_method == "average":
        for term_index in range(num_rows):
            score_agg[term_index] = np.mean(score_matrix[term_index])
    elif combination_method == "max":
        for term_index in range(num_rows):
            score_agg[term_index] = max(score_matrix[term_index])
    elif combination_method == "weighted_average":
        for term_index in range(num_rows):
            score_agg[term_index] = np.average(score_matrix[term_index], weights=weights)
    return score_agg


def get_feature_selection(tc_mat, vocabulary_inv_x, label_dist=None,
                          technique="mutual_information", combination_method="average"):
    """This function does feature selection corresponding to given term category 
    matrix - tc_mat. In th output feature_selection_score is a dictionary that 
    gives feature score corresponding to each word. With time more and more 
    different feature selection techniques can be added in this function.

    """
    if technique == "mutual_information":
        num_term = len(tc_mat)
        num_cat = len(tc_mat[0])
        sum_over_cat = np.zeros((num_term))
        sum_over_term = np.zeros((num_cat))
        N = 0  # Total number of terms
        for j, row in enumerate(tc_mat):
            sum_over_cat[j] = sum(row)
            for i, entry in enumerate(row):
                sum_over_term[i] += entry
                N += entry
        # N_10 matrix represents number of times given term is present but category is absent
        N_10 = np.zeros((num_term, num_cat))
        # N_10 matrix represents number of times given term is absent but category is present
        N_01 = np.zeros((num_term, num_cat))
        # N_10 matrix represents number of times given term is absent and category is absent
        N_00 = np.zeros((num_term, num_cat))
        for term_index in range(num_term):
            for cat_index in range(num_cat):
                N_10[term_index][cat_index] = sum_over_cat[
                    term_index] - tc_mat[term_index][cat_index]
                N_01[term_index][cat_index] = sum_over_term[
                    cat_index] - tc_mat[term_index][cat_index]
                N_00[term_index][cat_index] = N - tc_mat[term_index][cat_index] - \
                    N_10[term_index][cat_index] - N_01[term_index][cat_index]
        MI = np.zeros((num_term, num_cat))
        # Implementing the formula of mutual information
        for term_index in range(num_term):
            for cat_index in range(num_cat):
                if tc_mat[term_index][cat_index] != 0:
                    MI[term_index][cat_index] += (tc_mat[term_index][cat_index] * 1.0 / N) * math.log(
                        tc_mat[term_index][cat_index] * N * 1.0 / (sum_over_cat[term_index] * sum_over_term[cat_index]))
                if N_10[term_index][cat_index] != 0:
                    MI[term_index][cat_index] += (N_10[term_index][cat_index] * 1.0 / N) * math.log(
                        N_10[term_index][cat_index] * N * 1.0 / ((sum_over_cat[term_index]) * (N - sum_over_term[cat_index])))
                if N_01[term_index][cat_index] != 0:
                    MI[term_index][cat_index] += (N_01[term_index][cat_index] * 1.0 / N) * math.log(
                        N_01[term_index][cat_index] * N * 1.0 / ((N - sum_over_cat[term_index]) * (sum_over_term[cat_index])))
                if N_00[term_index][cat_index] != 0:
                    MI[term_index][cat_index] += (N_00[term_index][cat_index] * 1.0 / N) * math.log(N_00[term_index][
                        cat_index] * N * 1.0 / ((N - sum_over_cat[term_index]) * (N - sum_over_term[cat_index])))
        MI_agg = combine_feature_selection_scores(
            MI, weights=label_dist, combination_method=combination_method)
        feature_selection_score = {}
        for term_index in range(num_term):
            feature_selection_score[vocabulary_inv_x[term_index]] = MI_agg[term_index]
        sorted_feature = sorted(
            vocabulary_inv_x[:num_term], key=lambda x: feature_selection_score[x], reverse=True)
        sorted_feature_vocab = {x: i for i, x in enumerate(sorted_feature)}
        return [feature_selection_score, sorted_feature, sorted_feature_vocab]


def build_input_data(x_text, y_text, sorted_feature_vocab, vocabulary_y, num_feature=None):
    """Build input data

    x_text is 2D array of words of each product title and y_text is 1D array of 
    label strings. Output X is 2D matrix of size - (number of data points * size 
    of vocabulary) with the positions corresponding to which word has appeared 
    in product title filled with 1 and rest with 0. Output y is 1D array of 
    integers corresponding to labels

    """
    if not num_feature:
        num_feature = len(sorted_feature_vocab)
    num_samples = len(x_text)
    X = np.zeros((num_samples, num_feature))
    y = np.zeros((num_samples), dtype=np.int)
    for i, sentence in enumerate(x_text):
        for word in sentence:
            ftr_index = sorted_feature_vocab.get(word, num_feature + 1)
            if(ftr_index < num_feature):
                X[i][ftr_index] += 1
        y[i] = vocabulary_y[y_text[i]]
    return [X, y]


def pad_sentences(sentences, sequence_length, pad_value):
    """sentences here is expected to be 2D array of words (infact numbers 
    corresponding to words). Each sentence is padded with pad_value to make 
    of length sequence_length or trimmed to size sequence_length

    """
    sentences_padded = []
    for sentence in sentences:
        if len(sentence) > sequence_length:
            new_sentence = sorted(sentence)[:sequence_length]
            sentences_padded.append(new_sentence)
        else:
            num_padding = sequence_length - len(sentence)
            new_sentence = sentence + [pad_value] * num_padding
            sentences_padded.append(new_sentence)
    sentences_padded = np.array(sentences_padded)
    return sentences_padded


def load_train_data_for_cnn(x_text, y_text, num_feature=None, min_word_count=3,
                            max_title_length=100):
    """Load training data for Convolutional Neural Network. max_title_length is 
    the maximum length of input product title to be considered. x_text is 2D 
    array of words (string) of product titles. y_text is 1D array of product 
    labels (string). Only the words having total occurrence in input data greater 
    than min_word_count are considered. If num_feature is None, all the available 
    features are considered.

    """
    vocabulary_x, vocabulary_inv_x, vocabulary_y, vocabulary_inv_y, word_dist, label_dist = build_vocab(
        x_text, y_text)
    tc_mat = get_term_category_matrix(
        x_text, y_text, vocabulary_x, vocabulary_y, word_dist, min_word_count)
    feature_selection_score, sorted_feature, sorted_feature_vocab = get_feature_selection(
        tc_mat, vocabulary_inv_x, combination_method="max")
    if not num_feature:
        num_feature = len(sorted_feature_vocab)
    if num_feature > len(sorted_feature_vocab):
        num_feature = len(sorted_feature_vocab)
    x_tr = []
    y_tr = np.zeros((len(y_text), len(vocabulary_inv_y)), dtype=np.int)
    for sentence in x_text:
        data_vector = []
        for word in sentence:
            ftr_index = sorted_feature_vocab.get(word, num_feature + 1)
            if(ftr_index < num_feature):
                data_vector.append(ftr_index)
        x_tr.append(data_vector)
    for i, label in enumerate(y_text):
        y_tr[i][vocabulary_y[label]] = 1
    sequence_length = max(len(x) for x in x_tr)
    sequence_length = min([sequence_length, max_title_length])
    x_tr_padded = pad_sentences(x_tr, sequence_length, num_feature)
    vocabulary_inv_x_final = sorted_feature[:num_feature]
    vocabulary_inv_x_final.append(PADDING_WORD)
    vocabulary_x_final = {x: i for i, x in enumerate(vocabulary_inv_x_final)}
    return [x_tr_padded, y_tr, vocabulary_x_final, vocabulary_inv_x_final,
            vocabulary_y, vocabulary_inv_y, sequence_length]


def batch_iter(data, batch_size, num_epochs):
    """Generates a batch iterator for a dataset.

    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int(len(data) / batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        shuffle_indices = np.random.permutation(np.arange(data_size))
        shuffled_data = data[shuffle_indices]
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]


def get_data_vector(sentence, vocabulary, sequence_length):
    """Given the sentence and vocabulary return data vector in the format 
    required be CNN. sequence_length is the size of data vector to which it 
    is to be padded or trimmed.

    """
    sentence = clean_str(sentence)
    x_text = []
    for word in sentence.split():
        word = get_plural_free_word(word)
        val = vocabulary.get(word)
        if val:
            x_text.append(val)
    sentences_padded = pad_sentences([x_text], sequence_length, vocabulary[PADDING_WORD])
    return sentences_padded


def cnn_score_to_prob(score_dict):
    """This function converts scores given by CNN to probability values. Negative 
    scores are directly mapped to zero probability and positive scores are 
    normalized by sum of positive scores.

    """
    pos_score_dict = {key: max([value, 0]) for key, value in score_dict.items()}
    score_sum = sum(pos_score_dict.values())
    if score_sum == 0:
        score_sum = 1
    prob_dict = {key: value * 1.0 / score_sum for key, value in pos_score_dict.items()}
    return prob_dict


def probability_to_confidence_score(prob_array):
    """Given the array of probabilities, this function gives the confidence 
    score of max probability value. Value of alpha_parameter in implementation 
    is chosen based on hit and trial

    """
    alpha_parameter = 10
    exp_prob_array = [2**(alpha_parameter * item) for item in prob_array]
    confidence_score = max(exp_prob_array) / sum(exp_prob_array)
    return confidence_score
