"""
The code removes colors from a sentence using trie data structure
which stores prefixes of colours.
Input: List of colors and sentence
Output: Sentence after removing colours
"""
from Trie import Trie
import sys

colors = ['brown', 'maroon', 'multicolored', 'violet', 'navy', 'tan', 'light blue', 'cream', 'blue', 'peach', 'dark blue', 'purple', 'yellow', 'transparent', 'off white', 'black', 'orange', 'offwhite', 'red', 'pink', 'turquoise', 'khaki', 'off-white', 'white', 'multi', 'gunmetal', 'grey', 'multicolor', 'green', 'beige', 'light green', 'dark green','chocolate brown']

def searchPrefix(sentence):
	"""
	Creates a trie from list of colors.
	Uses this trie to remove color names from sentence
	"""
	db = Trie()
	for color in colors:
		db.insert(color)

	stringIndexed = sentence.split()
	index = 0
	while index < len(stringIndexed)-1:
		# print stringIndexed[index],index,stringIndexed[index+1]
		j = index
		# print index
		current = db.search(stringIndexed[index])
		if current:
			while(current and current.children and stringIndexed[j+1] in current.children):
				current = current.children[stringIndexed[j+1]]
				j = j + 1

			if current.end_node:
				del stringIndexed[index:j+1]
				# print stringIndexed
				# print index
				index = index - 1
			else:
				index = j + 1
				# print "index is",index
		else:
			index = index + 1

	return ' '.join(stringIndexed)

def main():
	# string = "The jeans is light chocolate brown in color and has brown pockets"
	string = sys.argv[1]
	filteredString = searchPrefix(string.lower())
	print filteredString

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")
	main()