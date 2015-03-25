from pymongo import MongoClient
import csv,json
from sklearn import feature_extraction
from sklearn import naive_bayes
from sklearn import metrics
from sklearn.svm import SVC
import scipy
import numpy as np
import re
import HTMLParser
import requests
from bs4 import BeautifulSoup
from nltk.tag import pos_tag # doctest: +SKIP
from nltk.tokenize import word_tokenize
import operator
from requests_oauthlib import OAuth1
import json
import urllib

Client=MongoClient()
db=Client['snapdeal']
products=db['products']
# test_products = db['test_products']

vocabulary={}
sentences={}
# oauth=OAuth1("dj0yJmk9TFdOamZHYmxsYVZLJmQ9WVdrOWVHdG9ORGxRTnpBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD02OA--","03fdab212c06f4134abd1e5dbf7eba2932450ac6")

def find_category(item_name, from_db=False):
	# print "finding category"
	category_identified=[""]
	# query=urllib.urlencode({'format':'json','q':item_name,'count':20})
	# query=query.replace('+','%20')
	# url="https://yboss.yahooapis.com/ysearch/web?"+query
	# print url
	# #     print (url)
	# if from_db and test_products.find_one({'item':item_name,'search.bossresponse.responsecode':'200'}):
	all_desc= products.find_one({'name':item_name}).get('search',{}).get('bossresponse',{}).get('web',{}).get('results',{})
	# else:
	# #         print item_name
	#     result=requests.get(url,auth=oauth)
	#     if 'error' in (result.json()):
	#         print (query)
	#         print (item_name)
	#         print (result.json())
	#         return category_identified[0]
	#     test_products.insert({'item':item_name,'search':result.json()})
	#     try:
	#         all_desc=result.json().get('bossresponse',{}).get('web',{}).get('results',{})
	#     except:
	#         print item_name
	# print "yahoo API done"
	# if all_desc:
	#         print all_desc
	test_vector=vectorizer.transform([""])
	for desc in all_desc:
	    desc_sentence=BeautifulSoup(desc['abstract']).text.encode('ascii','ignore').lower().replace(',',' , ')\
	    .replace(':',' : ').replace(';',' ; ').replace('"',' " ') #
	    test_vector=test_vector+vectorizer.transform([desc_sentence.lower()])
#         for y in np.nonzero(test_vector.toarray().astype(int)[0])[0]:
#             print vectorizer.get_feature_names()[y]
#         category_identified=clf.predict(test_vector)
#         print test_vector
	j=test_vector.toarray().astype(int)
	output_vector=[]
	for y in np.nonzero(j[0])[0]:
	    output_vector.append((vectorizer.get_feature_names()[y], j[0][y]))
	class_index=clf.predict_proba(test_vector).argmax()
	print clf.predict_proba(test_vector)
	return output_vector,clf.classes_[class_index]
	# print 'actual category',all_desc['delhivery_cat_id']
	

fetch_product = db.products.find({'yahoo_result.bossresponse.web.results':{'$exists':1}}).limit(1000)
count_product = 0
test = []
for product_info in fetch_product:
	# print product_info['name']
	product_name=product_info['name']
	count_product = count_product + 1
	if count_product > 800:
		test.append(product_name)
	count_temp_dict={}
	sentences[product_name]=[]
	if 'results' in product_info['yahoo_result']['bossresponse']['web']:
		for abstract in product_info['yahoo_result']['bossresponse']['web']['results']:
			desc_sentence=BeautifulSoup(abstract['abstract']).text.encode('ascii','ignore').lower().replace(',',' , ').replace(':',' : ').replace(';',' ; ').replace('"',' " ') 
			sentences[product_name].append(desc_sentence)
			words=desc_sentence.split()
			for word in words:
			    if word in count_temp_dict:
			        count_temp_dict[word]+=1
			    else:
			        count_temp_dict[word]=1

			words_shortlisted=count_temp_dict.keys()
			for word in words_shortlisted:
				if not re.match('^[a-zA-Z]+[^a-zA-Z]*[a-zA-Z]*$',word) or count_temp_dict[word]<=1:
				    del count_temp_dict[word]
			for word in count_temp_dict:
				if word in vocabulary:
				    vocabulary[word]+=1
				else:
				    vocabulary[word]=1

print len(vocabulary)
# print vocabulary
vectorizer=feature_extraction.text.CountVectorizer(vocabulary=set(vocabulary),ngram_range=(1,1),stop_words='english')

# print vectorizer
f=open("category_tree.json")
category_map=json.load(f)
# print category_map
x_train=[]
y_train=[]

count_training = 0

trainingData = db.products.find({'yahoo_result.bossresponse.web.results':{'$exists':1}}).limit(1000)
for product_info in trainingData:
	count_training = count_training + 1
	if(count_training > 800):
		break
	# print product_info['name']
	x_train.append(product_info['name'])
	# print product_info['delhivery_cat_id']
	delhivery_cat_id=str(product_info['delhivery_cat_id'])
	y_train.append(category_map[delhivery_cat_id]['category'])
x_train_transformed=vectorizer.transform(x_train)

print 'x train length',len(x_train)
print 'y train length',len(y_train)

#Naive Bayes Classifer
clf=naive_bayes.MultinomialNB(fit_prior=False)
clf.fit(x_train_transformed,y_train)

#SVM Classifier
clf=SVC(C=10,probability=True)
clf.fit(x_train_transformed,y_train)

for data in test:
	x=find_category(data,True)
	print x[1],sorted(x[0],key=lambda z :z[1], reverse=True)