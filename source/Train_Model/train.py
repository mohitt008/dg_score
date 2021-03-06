__author__ = 'rohan'

import sys
import json
import os.path
import data_utils
import tensorflow as tf
from text_cnn import TextCNN
from removeColor import removeColor
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname('__file__')))
print PARENT_DIR
sys.path.append(PARENT_DIR)
#from xgboost import XGBClassifier

import re
#from Load_Data.get_products import get_categories, get_delhivery_products, get_vendor_category_products, get_delhivery_vendor_products
from config.config_details import second_level_cat_names, words_to_remove, ROOT_PATH, cnn_params, train_data_file_path
#from utilities import get_category_tree

import csv
#import json
#import numpy as np
#from pymongo import MongoClient

from sklearn import feature_extraction
from sklearn import naive_bayes
#from sklearn import metrics
#from sklearn.svm import SVC
#from sklearn.svm import LinearSVC
#from sklearn import tree
#from sklearn.ensemble import RandomForestClassifier
#from nltk.stem.porter import PorterStemmer
#from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_selection import SelectPercentile, chi2, f_classif, SelectFpr
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib


plural_dict = {}
with open(ROOT_PATH + '/data/word_list_verified.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[2] != '0':
            plural_dict[row[0]] = row[1]

# client = MongoClient()
# db = client['cat_identification']
# product_table = db['products_new']


def mypluralremover(word):
    """

    :param word:  the word to remove plural from
    :return: the singular verson of the word
    """
    # if word == "men's" or word == "men":
    #     return "man"
    # elif word == "women's" or word == "women":
    #     return "woman"
    # elif word.endswith == "'s":
    #     return word[:-2]
    # elif word.endswith('ies') and len(word) >= 5:
    #     return word[:-3] + "y"
    # elif word.endswith('ves') and len(word) >= 5:
    #     return word[:-3] + "f"
    # elif (word.endswith('ches') or word.endswith('sses') or word.endswith('shes') or word.endswith('xes')) and len(word) >=5:
    #     return word[:-2]
    # elif word.endswith('ss'):
    #     return word
    # elif word.endswith('s') and len(word) >= 4:
    #     return word[:-1]
    # else:
    #     return word
    # if word.endswith('ves'):
    #     return word[:-1]
    # else:
    #     return singularize(word)
    if word.endswith('s') or word.endswith('S'):
        if word in plural_dict:
            return plural_dict[word]
        else:
            return word
    else:
        return word


def ngrams(desc, MIN_N=2, MAX_N=5):
    """
    :param desc: word to find ngrams from
    :param MIN_N: the minimum n gram
    :param MAX_N: the maximum n gram
    :return: list of all ngrams
    """

    ngram_list = []
    desc = remove_text_inside_brackets(desc)
    desc = removeColor(desc)
    tokens = re.findall(r"[\w'-]+", desc)
    tokens = [mypluralremover(x) for x in tokens]

    try:
        if tokens != []:
            if len(tokens) < 2:
                ngram_list.append(" ".join(tokens))
            else:
                n_tokens = len(tokens)
                for i in xrange(n_tokens):
                    for j in xrange(i + MIN_N, min(n_tokens, i + MAX_N) + 1):
                        ngram_list.append(" ".join(tokens[i:j]))
    except Exception as e:
        print desc
        print e
    return ngram_list


def remove_text_inside_brackets(text, brackets="()[]"):
    # TODO Optimize this function
    """

    :param text:
    :param brackets:
    :return:
    """
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1) ** is_close  # `+1`: open, `-1`: close
                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0
                break
        else:  # character is not a bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)


#
# def get_products(cat_id, count):
#
#     return get_delhivery_products(cat_id,count)

def train_cnn(x_train, y_train, vocab_length, num_classes, model_path):
    """Train CNN using x_train and y_train and save the model at model_path

    """
    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=cnn_params['allow_soft_placement'],
            log_device_placement=cnn_params['log_device_placement'])
        sess = tf.Session(config=session_conf)
        with sess.as_default():
            cnn = TextCNN(
                sequence_length=x_train.shape[1],
                num_classes=num_classes,
                vocab_size=vocab_length,
                embedding_size=cnn_params['embedding_dim'],
                filter_sizes=cnn_params['filter_sizes'],
                num_filters=cnn_params['num_filters'],
                l2_reg_lambda=cnn_params['l2_reg_lambda'])

            # Define Training procedure
            global_step = tf.Variable(0, name="global_step", trainable=False)
            optimizer = tf.train.AdamOptimizer(1e-4)
            grads_and_vars = optimizer.compute_gradients(cnn.loss)
            train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)

            # Summaries for loss and accuracy
            loss_summary = tf.scalar_summary("loss", cnn.loss)
            acc_summary = tf.scalar_summary("accuracy", cnn.accuracy)

            saver = tf.train.Saver(tf.all_variables())

            # Initialize all variables
            sess.run(tf.initialize_all_variables())

            # Generate batches
            batches = data_utils.batch_iter(zip(x_train, y_train), cnn_params[
                                            'batch_size'], cnn_params['num_epochs'])
            # Training loop. For each batch...
            for batch in batches:
                x_batch, y_batch = zip(*batch)
                feed_dict = {
                    cnn.input_x: x_batch,
                    cnn.input_y: y_batch,
                    cnn.dropout_keep_prob: cnn_params['dropout_keep_prob']
                }
                _, step, loss, accuracy = sess.run(
                    [train_op, global_step, cnn.loss, cnn.accuracy], feed_dict)
                if step % 100 == 0:
                    print("step {}, loss {:g}, train_acc {:g}".format(step, loss, accuracy))
            path = saver.save(sess, model_path)
            print("Saved CNN model to {}\n".format(path))


def root_training_prcoess():
    # count=1000
    # category_tree=get_category_tree()
    # category_list=category_tree.keys()
    # product_list=[]
    category_count_dict = {}
    # second_level_categories=set()
    train_x = []
    train_y = []
    # # print category_list
    # # import pdb;pdb.set_trace()
    # For vendor based model
    """
    total=0
    for category_id in category_list:
        current_prod_list=json.loads(get_products(category_id,count=count))
        print category_id
        total=total+ len(current_prod_list)
        print total
        # print current_prod_list
        current_prod_count=len(current_prod_list)
        category_count_dict[category_id]=current_prod_count
        # print category_count_dict
        current_category_name="Delhivery_Others"
        if current_prod_count>=800:
            current_category_name=category_id
            second_level_categories.add(category_id)
        for products in current_prod_list:
            # print products
            train_x.append(products.get('product_name',"").encode('ascii','ignore').lower())
            train_y.append(current_category_name)
            product_list.append((products,current_category_name))
    """
    # hq = product_table.find({"vendor_id":"HQ"})
    print "----------------"
    print "root training"

    print "Training CNN"
    model_path = ROOT_PATH + "/data/Models/clf_cnn.ckpt"
    vocab_path = ROOT_PATH + "/data/Models/clf_cnn_vocab.txt"
    x_tr_text, y_tr_text = data_utils.read_data_and_labels(train_data_file_path)
    x_train, y_train, vocabulary, vocabulary_inv, vocabulary_y, vocabulary_inv_y, sequence_length = data_utils.load_train_data_for_cnn(
        x_tr_text, y_tr_text, num_feature=cnn_params['num_feature'],
        min_word_count=cnn_params['min_word_count'],
        max_title_length=cnn_params['max_title_length'])
    print "Train data size: {}, Num Category: {}, vocab_size: {}, seq_length: {}".format(
        len(x_train), len(vocabulary_y), len(vocabulary), sequence_length)
    train_cnn(x_train, y_train, len(vocabulary), len(vocabulary_y), model_path)
    data = {'vocabulary_x': vocabulary, 'vocabulary_inv_y': vocabulary_inv_y,
            'sequence_length': sequence_length}
    json.dump(data, open(vocab_path, 'w'))
    print "CNN Training Done"
    # print hq.count()
    # for products in hq:
    #     train_x.append(products['product_name'].encode('ascii','ignore').lower())
    #     if products['vendor_category_id'] == 'NA':
    #         current_category_name = 'Delhivery_Others'
    #     else:
    #         current_category_name =  products['vendor_category_id'].split('->')[0]
    #     train_y.append(current_category_name)
    #     product_list.append((products,current_category_name))

    # Reading from csv
    reader = csv.DictReader(open(train_data_file_path))
    for row in reader:
        if row['new_cat'] != 'Unclear':
            try:
                ngram_list = ngrams(row['product_name'].encode('ascii', 'ignore').lower(), 1, 1)
                train_x.append(" ".join(ngram_list))
                train_y.append(row['new_cat'])
            except Exception:
                pass
    # train_x,train_y=train_x[:10000],train_y[:10000]
    print "Training Set Constructed"
    print "Training Set Stats"
    print category_count_dict
    print len(train_x), len(train_y)
    # train_x_tokenized=[]

    # for records in train_x:
    #     tokens=ngrams(records.lower(),1,3)
    #     if tokens:
    #         train_x_tokenized.append(tokens)
    #     else:
    # #         print records
    #         train_x_tokenized.append([""])
    # print "Tokenized Training Set"

    vocabulary = set()
    print "Constructing Vocab"
    for i, records in enumerate(train_x):
        # print i
        try:
            for word in ngrams(records.lower(), 1, 3):
                if not re.match('^[0-9]+$', word):
                    vocabulary.add(word.lower())
        except Exception as e:
            print e
            print i, records
            pass
    print "Vocab Done"
    for word in words_to_remove:
        try:
            vocabulary.remove(word)
        except Exception:
            pass

    vectorizer = feature_extraction.text.CountVectorizer(
        vocabulary=set(vocabulary), ngram_range=(1, 3), stop_words='english')
    train_x_vectorized = vectorizer.transform(train_x)

    clf_bayes = naive_bayes.MultinomialNB(fit_prior=False)
    clf_bayes.fit(train_x_vectorized, train_y)

    print "model 1 done"

    clf_chi = Pipeline([
        ('feature_selection', SelectPercentile(chi2, 20)),
        ('classification', naive_bayes.MultinomialNB(fit_prior=False))])
    clf_chi.fit(train_x_vectorized, train_y)

    print "model 2 done"

    clf_fp = Pipeline([
        ('feature_selection', SelectFpr(f_classif, alpha=0.1)),
        ('classification', naive_bayes.MultinomialNB(fit_prior=False))])
    clf_fp.fit(train_x_vectorized, train_y)

    print "model 3 done"

    print os.path.dirname(os.path.realpath('__file__')) + '/../Models/clf_bayes.pkl'
    joblib.dump(clf_bayes, ROOT_PATH + '/data/Models/clf_bayes.pkl')
    joblib.dump(clf_chi, ROOT_PATH + '/data/Models/clf_chi.pkl')
    joblib.dump(clf_fp, ROOT_PATH + '/data/Models/clf_fp.pkl')
    joblib.dump(vectorizer, ROOT_PATH + '/data/Models/vectorizer.pkl')

    # joblib.dump(second_level_cats,'../Models')


def second_training_process():
    # count=20000
    """
    category_tree=json.loads(get_categories())
    for parent_category in second_level_cat_names:
        train_x=[]
        train_y=[]
        total=0
        category_count_dict={}
        for category_id in category_tree[parent_category].keys():
            ## For vendor based model

            print get_products(category_id,count)
            current_prod_list=json.loads(get_products(category_id,count=count))
            print category_id
            total=total+ len(current_prod_list)
            print total
            # print current_prod_list
            current_prod_count=len(current_prod_list)
            category_count_dict[category_id]=current_prod_count
            # print category_count_dict
            current_category_name="Delhivery_Others"
            if current_prod_count>=500:
                current_category_name=category_id
            for products in current_prod_list:
                # print products
                train_x.append(products.get('product_name',"").encode('ascii','ignore').lower())
                train_y.append(current_category_name)
            try:
                hq = product_table.find({"vendor_id":"HQ","vendor_category_id":category_id})
                print "---------------------"
                print category_id,hq.count()
                print "---------------------"
                for products in hq:
                    train_x.append(products['product_name'].encode('ascii','ignore').lower())
                    current_category_name =  category_id
                    train_y.append(current_category_name)
                    # product_list.append((products,current_category_name))
            except:
                pass
            """
    # category_tree=get_category_tree()
    for parent_category in second_level_cat_names:
        train_x = []
        train_y = []
        train_x_cnn = []
        reader = csv.DictReader(open(train_data_file_path))
        for row in reader:
            if row['new_cat'] != 'Unclear' and row['new_cat'] == parent_category and row['new_subcat'] != 'null' and row['new_subcat'] != '':
                try:
                    ngram_list = ngrams(row['product_name'].encode('ascii', 'ignore').lower(), 1, 1)
                    train_x.append(" ".join(ngram_list))
                    train_y.append(row['new_subcat'])
                    sentence = data_utils.clean_str(
                        row['product_name'])
                    train_x_cnn.append(sentence.split())
                except Exception:
                    pass

        print "Training Set Constructed for %s " % (parent_category)
        print "Training Set Stats"
        print len(train_x), len(train_y)
        print "Training CNN"
        model_path = ROOT_PATH + "/data/Models/SubModels/clf_cnn_" + \
            parent_category.replace(' ', '_')
        vocab_path = ROOT_PATH + "/data/Models/SubModels/clf_cnn_" + \
            parent_category.replace(' ', '_') + "_vocab.txt"
        x_train, y_train, vocabulary, vocabulary_inv, vocabulary_y, vocabulary_inv_y, sequence_length = data_utils.load_train_data_for_cnn(
            train_x_cnn, train_y, num_feature=cnn_params['num_feature'],
            min_word_count=cnn_params['min_word_count'],
            max_title_length=cnn_params['max_title_length'])
        print "Train data size: {}, Num Category: {}, vocab_size: {}, seq_length: {}".format(
            len(x_train), len(vocabulary_y), len(vocabulary), sequence_length)
        train_cnn(x_train, y_train, len(vocabulary), len(vocabulary_y), model_path)
        data = {'vocabulary_x': vocabulary, 'vocabulary_inv_y': vocabulary_inv_y,
                'sequence_length': sequence_length}
        json.dump(data, open(vocab_path, 'w'))
        print "CNN Training Done"

        vocabulary = set()
        print "Constructing Vocab"
        for i, records in enumerate(train_x):
            # print i
            # print records
            try:
                for word in ngrams(records.lower(), 1, 3):
                    if not re.match('^[0-9]+$', word):
                        vocabulary.add(word.lower())
            except Exception as e:
                print e
                print records
                pass
        print "Vocab Done"

        for word in words_to_remove:
            try:
                vocabulary.remove(word)
            except Exception:
                pass

        vectorizer = feature_extraction.text.CountVectorizer(
            vocabulary=set(vocabulary), ngram_range=(1, 3), stop_words='english')
        train_x_vectorized = vectorizer.transform(train_x)

        clf_bayes = naive_bayes.MultinomialNB(fit_prior=False)
        clf_bayes.fit(train_x_vectorized, train_y)

        joblib.dump(vectorizer, ROOT_PATH + "/data/Models/SubModels/Vectorizer_" + parent_category)
        joblib.dump(clf_bayes, ROOT_PATH + "/data/Models/SubModels/clf_bayes_" + parent_category)

        if parent_category in second_level_cat_names:
            clf_fpr = Pipeline([
                ('feature_selection', SelectFpr(f_classif, 0.05)),
                ('classification', naive_bayes.MultinomialNB(fit_prior=False))])
            clf_fpr.fit(train_x_vectorized, train_y)
            joblib.dump(clf_fpr, ROOT_PATH + "/data/Models/SubModels/clf_fpr_" + parent_category)

if __name__ == '__main__':
    root_training_prcoess()
    second_training_process()
    # categories=json.loads(get_categories())
    # for cat in categories:
    #     print cat
    #     for subcats in categories[cat]:
    #         print '\t'+subcats
