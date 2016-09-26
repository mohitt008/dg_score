import numpy as nm
import pandas as pd
from pprint import pprint
from time import time
import logging
import sklearn.cross_validation
import sklearn.feature_extraction.text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.decomposition import PCA
import sklearn.metrics
from sklearn.feature_selection import VarianceThreshold
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn import linear_model
from sklearn.feature_selection import RFECV
#import sklearn.neural_network.MLPClassifier

import csv
import nltk.stem
english_stemmer = nltk.stem.SnowballStemmer('english')
class StemmedCountVectorizer(CountVectorizer):
	def build_analyzer(self):
		analyzer = super(StemmedCountVectorizer,self).build_analyzer()
		return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))

"""
names = ['prd','client','cat','subcat','dg']
data = pd.read_csv("final_all_training_data_60-40.csv")


train,test = sklearn.cross_validation.train_test_split(data, train_size= .7)
train_data1, test_data1 = pd.DataFrame(train, columns= names), pd.DataFrame(test, columns = names)
train_data= train_data1[train_data1.prd.notnull()]
test_data= test_data1[test_data1.prd.notnull()]
"""
import random as r



names = ['prd','client','cat','subcat','dg']
f= open("New_Final_all_training_data_50-50.csv")
f.next()
f_reader = csv.reader(f)
f1= open("classified_unique_DG_test_data.csv")
f1.next()
f1_reader = csv.reader(f1)
#data = pd.read_csv("final_all_training_data.csv")
test = []
train = []
test_data=[]
train_data=[]
for rows in f_reader:
	train.append(rows)

for rows in f1_reader:
	test.append(rows)

train_label = []
test_label = []
for rows in train:
	x = rows[0]+' '+rows[1]
	train_data.append(x)
	train_label.append(rows[4])

for rows in test:
	x = rows[0]+' '+rows[1]
	test_data.append(x)
	test_label.append(rows[5])
#define a pipeline combining a text extractor with a simple
#classifier
pipeline= Pipeline([
	('vect',StemmedCountVectorizer(stop_words= None,ngram_range=(1,3))),
	('tfidf',sklearn.feature_extraction.text.TfidfTransformer(norm='l2',use_idf=False,smooth_idf =True,sublinear_tf=True)),
	('f_sel',VarianceThreshold()),
	('clf',LinearSVC()),
	])

#rfecv= RFECV(estimator=pipeline, step=1,
#             scoring='accuracy')

#uncommenting more parameters will give better exploring power but will 
#increase processing time in a comninatorial way
#parameters={
#	'vect__ngram_range':((1,3)),
#	'tfidf__norm':('l2'),
#	'vect__stop_words': (None),
#	'clf__class_weight': ({dict,'balanced'})
#}

#find the best parameters for both feature extraction and the classifier
#grid_search = GridSearchCV(pipeline,parameters,n_jobs=-1,verbose=1)

#print ("Perfoming grid search....")
#print("pipeline:",[name for name, _ in pipeline.steps])
#print("parameters:")
#pprint(parameters)
t0= time()

"""
train_cat = []
test_cat =[]
for rows in train_data['dg']:
	train_cat.append(rows)

for rows in test_data['dg']:
	test_cat.append(rows)

train_cat = tuple(train_cat)
test_cat = tuple(test_cat)

"""
vectorizer =sklearn.feature_extraction.text.CountVectorizer(stop_words= None,ngram_range=(1,3))
print "final_all_training_data again"
print "classificaion in mode_of_transport is going on"
#X_vectorized = vectorizer.fit_transform(train_data)
#a= vectorizer.vocabulary_
pipeline.fit(train_data,train_label)
#a= pipeline.get_params()['vect']
print("done in %0.3fs"%(time()-t0))
print ()
#print("Optimal number of features : %d" % rfecv.n_features_)

#print("Best score: %0.3f" % grid_search.best_score_)
#print("Best parameters set:")
#best_parameters = grid_search.best_estimator_.get_params()
#for param_name in sorted(parameters.keys()):
#	print("\t%s: %r" %(param_name,best_parameters[param_name]))
#vect = sklearn.feature_extraction.text.CountVectorizer(stop_words= None,ngram_range=(1,3),vocabulary=a)
#x_test = vectorizer.transform(test_data)
x_test= test_data
predict_cat = pipeline.predict(x_test)
cat_confidence = pipeline.decision_function(x_test)
print "classification in mode_of_transport is done"

#accuracy_cat = pipeline.score(test_matrix,test_cat)
precision, recall, f1, _ = sklearn.metrics.precision_recall_fscore_support(test_label,predict_cat)

n_data=[]
for i,x in enumerate(test):
	y= x + [predict_cat[i]] + [cat_confidence[i]]
	n_data.append(y)
"""
writer = csv.writer(open('Refined_Result_DG_test_data_with_confidence.csv','w'))
writer.writerow(['prd','client','cat','subcat','cat_confidence','dg_ruleEngine','dg_keyword','dg_ML','dg_confidence'])
for row in n_data:
	writer.writerow(row)
"""
print sklearn.metrics.classification_report(test_label,predict_cat)

print "classification in mode_of_transport is done"
#print ("accuracy = ",accuracy_cat)
print ("precision =", (precision))
print ("recall =", (recall))
print ("f_score =",(f1))



