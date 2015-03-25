# -*- coding: utf-8 -*-
from nltk import word_tokenize,pos_tag,FreqDist
from nltk.stem.porter import PorterStemmer
import removeTags 
import re
import sys
import random
from pymongo import MongoClient

database = "snapdeal"
collection = "products"
client = MongoClient()

if database not in client.database_names():
		raise Exception("Database does not exists")
db = client[database]

if collection not in db.collection_names():
		raise Exception("Collection does not exists")
products = db[collection]

class Sentence:
	
	def __init__(self,sentence):
		self.sentence = sentence
		self.stemmed = PorterStemmer()

	def removeHTMLTags(self,paragraph):

		"""
		Input: paragraph (string)
		Given a paragarpah remove HTML tags like <b> </b>
		"""
		return removeTags.strip_tags(paragraph)

	def removeSplChars(self,data):

		"""
		Input: string
		From HTML-free paragraph, remove special characters like >> ?
		"""
		pattern=re.compile("[^\w']")
		return pattern.sub(' ',data)

	def stemmer(self,unprocessedNouns):

		"""
		Input: List of strings
		perform stemming on tokens(unprocessedNouns)
		"""
		nouns = []
		for word in unprocessedNouns:
			nouns.append(self.stemmed.stem(word))
		return nouns

	def getNouns(self):

		"""
		extract noun from abstracts and calculate the 
		frequency of common noun for each product
		"""
		# remove HTML tags if any from paragraph
		processedHTML = self.removeHTMLTags(self.sentence)
		# remove special characters from paragraph
		processedSplChars = self.removeSplChars(processedHTML)
		# tokenize sentences into words
		tokens = word_tokenize(processedSplChars)
		# postag words
		tagged = pos_tag(tokens)
		# select and convert words to lower case: NN for singular common nouns, NNS for plural common nouns
		unprocessedCommonNouns = [word.lower() for word,pos in tagged \
				if (pos == 'NN' or pos == 'NNS')]
		# apply stemming on nouns
		stemmedCommonNouns  = self.stemmer(unprocessedCommonNouns)
		# count frequency of each word
		CommontagDist = FreqDist(word for word in stemmedCommonNouns)
	
		return CommontagDist.most_common()


if __name__ == '__main__':

	delID = int(sys.argv[1])
	if products.find({"delhivery_cat_id":delID}).count() == 0:
		raise Exception("Category does not exist")

	items = products.find({"delhivery_cat_id":delID},{"name":1,'yahoo_result.bossresponse.web.results.abstract':1})
	for item in items:
		paragraph = []
		if 'results' in item['yahoo_result']['bossresponse']['web']:
			for abstract in item['yahoo_result']['bossresponse']['web']['results']:
				paragraph.append(abstract['abstract'])
			para =  '. '.join(paragraph)
			tokenize = Sentence(para)
			nounFreq = tokenize.getNouns()