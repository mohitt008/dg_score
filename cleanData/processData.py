# -*- coding: utf-8 -*-
from nltk import word_tokenize,pos_tag,FreqDist
from nltk.stem.porter import PorterStemmer
import removeTags 
import re
import sys

class Sentence:
	
	def __init__(self,sentence):
		self.sentence = sentence
		self.nouns = []
		self.stemmed = PorterStemmer()
		self.processedHTML = str()
		self.processedSplChars = str()
		self.tokens = []
		self.tagged = []
		self.unprocessedNouns = []
		self.tagDist = []
		self.stemmedNouns = []

	def removeHTMLTags(self,paragraph):
		## remove HTML tags like <b> </b>
		return removeTags.strip_tags(paragraph)

	def removeSplChars(self,data):
		## remove special characters like >> ?
		pattern=re.compile("[^\w']")
		return pattern.sub(' ',data)

	def stemmer(self,unprocessedNouns):
		## perform stemming on words
		for word in self.unprocessedNouns:
			self.nouns.append(self.stemmed.stem(word))
		return self.nouns

	def getNouns(self):
		##	extract noun from sentences and caculate the frequency
		# remove HTML tags if any from paragraph
		self.processedHTML = self.removeHTMLTags(self.sentence)
		# remove special characters from paragraph
		self.processedSplChars = self.removeSplChars(self.processedHTML)
		# tokenize sentences into words
		self.tokens = word_tokenize(self.processedSplChars)
		# postag words
		self.tagged = pos_tag(self.tokens)
		# select and convert words to lower case: NN for singular common nouns, NNS for plural common nouns, NNP for singular proper nouns, NNPS for plural proper noun
		self.unprocessedNouns = [word.lower() for word,pos in self.tagged \
				if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
		# apply stemming on nouns
		self.stemmedNouns  = self.stemmer(self.unprocessedNouns)
		# count frequency of each word
		self.tagDist = FreqDist(word for word in self.stemmedNouns)
		print self.tagDist.most_common()

if __name__ == '__main__':
	tokenize = Sentence(sys.argv[1])
	tokenize.getNouns()
	# tokenize2 = Sentence("iPhone6 is really good.")
	# tokenize2.getNouns()