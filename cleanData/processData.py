# -*- coding: utf-8 -*-
from nltk import word_tokenize,pos_tag,FreqDist
from nltk.stem.porter import PorterStemmer
import removeTags 
import re

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
		print "processedSentence1",processedSentence1
		# remove special characters from paragraph
		processedSentence2 = self.removeSplChars(processedSentence1)
		print "processedSentence2",processedSentence2
		# tokenize sentences into words
		tokens = word_tokenize(processedSentence2)
		print "tokens",tokens	
		# postag words
		tagged = pos_tag(tokens)
		print "tagged",tagged
		# select NN for singular common nouns, NNS for plural common nouns, NNP for singular proper nouns, NNPS for plural proper noun
		unprocessedNouns = [word.lower() for word,pos in tagged \
				if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
		print "unprocessedNouns",unprocessedNouns
		# apply stemming on nouns
		processedNouns  = self.stemmer(unprocessedNouns)
		print "processedNouns",processedNouns
		# count frequency of each word
		tag_fd = FreqDist(word for word in processedNouns)
		# print tag_fd.most_common()

if __name__ == '__main__':
	tokenize = preProcess()
	tokenize.getNouns('Home » Eyeglasses » Unisex eyeglasses » Rimless » Vincent chase » <b>Vincent chase vc 0315 silver sky blue white aoyo eyeglasses</b>; Problem in placing order ?,<b>vincent-chase-vc-0315-silver-sky-blue-white-aoyo-eyeglasses</b> ...,Shop online for latest collection of Vincent Chase frames for men and women with a collection of 800+ Vincent Chase Eyeglasses frames, Free Shipping 14 Days ...,<b>vincent-chase-vc-0315-silver-sky-blue-white-aoyo-eyeglasses</b>. Rs 2489 (60%) Rs 990. vincent-chase-vc0323-gunmetal-black-silver-5150-eyeglasses (1) Rs 1998 (75%) Rs 499.')