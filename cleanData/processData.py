# -*- coding: utf-8 -*-
from nltk import word_tokenize,pos_tag,FreqDist
from nltk.stem.porter import PorterStemmer
import removeTags 
import re
import sys

class preProcess:
	
	def __init__(self):
		self.nouns = []

	def removeHTMLTags(self,paragraph):
		## remove HTML tags like <b> </b>
		return removeTags.strip_tags(paragraph)

	def removeSplChars(self,data):
		## remove special characters like >> ?
		pattern=re.compile("[^\w']")
		return pattern.sub(' ',data)

	def stemmer(self,unprocessedNouns):
		## perform stemming on words
		stemmed = PorterStemmer()
		for word in unprocessedNouns:
			self.nouns.append(stemmed.stem(word))
		return self.nouns

	def getNouns(self,sentence):
		##	extract noun from sentences and caculate the frequency

		# remove HTML tags if any from paragraph
		processedSentence1 = self.removeHTMLTags(sentence)
		# remove special characters from paragraph
		processedSentence2 = self.removeSplChars(processedSentence1)
		# tokenize sentences into words
		tokens = word_tokenize(processedSentence2)
		# postag words
		tagged = pos_tag(tokens)
		# select and convert words to lower case: NN for singular common nouns, NNS for plural common nouns, NNP for singular proper nouns, NNPS for plural proper noun
		unprocessedNouns = [word.lower() for word,pos in tagged \
				if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
		# apply stemming on nouns
		processedNouns  = self.stemmer(unprocessedNouns)
		# count frequency of each word
		tag_fd = FreqDist(word for word in processedNouns)
		print tag_fd.most_common()

if __name__ == '__main__':
	tokenize = preProcess()
	tokenize.getNouns(sys.argv[1])