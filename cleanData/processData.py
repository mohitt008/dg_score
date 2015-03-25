# -*- coding: utf-8 -*-
from nltk import word_tokenize,pos_tag,FreqDist
from nltk.stem.porter import PorterStemmer
import removeTags 
import re
import sys
import random
from pymongo import MongoClient

client = MongoClient()
db = client['snapdeal']
products = db['products']

class Sentence:
	
	def __init__(self,sentence):
		self.sentence = sentence
		self.stemmed = PorterStemmer()

	def removeHTMLTags(self,paragraph):

		"""
		remove HTML tags like <b> </b>
		"""
		return removeTags.strip_tags(paragraph)

	def removeSplChars(self,data):

		"""
		remove special characters like >> ?
		"""
		pattern=re.compile("[^\w']")
		return pattern.sub(' ',data)

	def stemmer(self,unprocessedNouns):

		"""
		perform stemming on words
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
	
		print "Common Noun:",CommontagDist.most_common()
		print "============================================================================="


if __name__ == '__main__':

	delID = int(sys.argv[1])
	if products.find({"delhivery_cat_id":delID}).count() == 0:
		print "Category {} does not exist".format(delID)
		sys.exit(0)
	items = products.find({"delhivery_cat_id":delID},{"name":1,'yahoo_result.bossresponse.web.results.abstract':1})
	for item in items:
		paragraph = []
		print item['name']
		if 'results' in item['yahoo_result']['bossresponse']['web']:
			for abstract in item['yahoo_result']['bossresponse']['web']['results']:
				paragraph.append(abstract['abstract'])
			para =  '. '.join(paragraph)
			print '------------------------'
			tokenize = Sentence(para)
			tokenize.getNouns()