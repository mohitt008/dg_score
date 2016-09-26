import numpy as nm
import pandas as pd
from pprint import pprint
from time import time
import logging
import sklearn.cross_validation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest
from sklearn.decomposition import PCA
import sklearn.metrics
from sklearn.feature_selection import VarianceThreshold
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn import linear_model
from sklearn.feature_selection import RFECV
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from mlxtend.preprocessing import DenseTransformer
#import sklearn.neural_network.MLPClassifier

import csv
import random as r



names = ['prd','client','cat','subcat','dg']
f= open("final_all_training_data.csv")
f.next()
f_reader = csv.reader(f)
#data = pd.read_csv("final_all_training_data.csv")
test = []
train = []
test_data=[]
train_data=[]
for rows in f_reader:
	x = r.randrange(1,11)
	if x <= 7:
		train.append(rows)
	else:
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
	test_label.append(rows[4])

#train,test = sklearn.cross_validation.train_test_split(data, train_size= .7)
#train_data1, test_data1 = pd.DataFrame(train, columns= names), pd.DataFrame(test, columns = names)
#train_data= train_data1[train_data1.prd.notnull()]
#test_data= test_data1[test_data1.prd.notnull()]

#define a pipeline combining a text extractor with a simple
#classifier
combined_features = FeatureUnion([
	#('univ_select',SelectKBest(chi2)),
	('f_sel',VarianceThreshold())
	])
pipeline= Pipeline([
	('vect_tfid',Pipeline([
		('vect',CountVectorizer(ngram_range = (1,3))),
		('tfidf',TfidfTransformer(norm='l2',use_idf=False,smooth_idf =True,sublinear_tf=True))
		])),
	#('to_dense', DenseTransformer()),
	('feature_Sel',combined_features),
	('clf',LinearSVC()),
	])



#uncommenting more parameters will give better exploring power but will 
#increase processing time in a comninatorial way
parameters={
	#'vect_tfid__vect__analyzer':('char','char_wb'),
	#'vect_tfid__vect__preprocessor':(callable,None),
	#'vect_tfid__vect__tokenizer':(callable,None),
	#'vect_tfid__vect__lowercase':(True,False),
	#'vect_tfid__vect__ngram_range':((1,2),(1,3)),
	'vect_tfid__tfidf__use_idf' : (True,False),
	#'vect_tfid__tfidf__smooth_idf' : (True,False),
	#'vect_tfid__tfidf__sublinear_tf' : (True,False),
	#'vect_tfid__tfidf__norm':('l1','l2',None),
	#'vect_tfid__vect__stop_words': ('english',None),

}

#find the best parameters for both feature extraction and the classifier
grid_search = GridSearchCV(pipeline,parameters,n_jobs=-1,verbose=1)

print ("Perfoming grid search....")
print("pipeline:",[name for name, _ in pipeline.steps])
print("parameters:")
pprint(parameters)
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

print "classificaion in mode_of_transport is going on"
grid_search.fit(train_data,train_label)



print("done in %0.3fs"%(time()-t0))
print ()

print("Best score: %0.3f" % grid_search.best_score_)
print("Best parameters set:")
best_parameters = grid_search.best_estimator_.get_params()
for param_name in sorted(parameters.keys()):
	print("\t%s: %r" %(param_name,best_parameters[param_name]))

predict_cat = grid_search.best_estimator_.predict(test_data)
print "classification in mode_of_transport is done"

#accuracy_cat = classifier.score(test_matrix,test_cat)
precision, recall, f1, _ = sklearn.metrics.precision_recall_fscore_support(test_cat,predict_cat)

print sklearn.metrics.classification_report(test_label,predict_cat)

print "classification in mode_of_transport is done"
#print ("accuracy = ",accuracy_cat)
print ("precision =", nm.mean(precision))
print ("recall =", nm.mean(recall))
print ("f_score =",nm.mean(f1))



