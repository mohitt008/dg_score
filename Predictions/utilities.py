# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


class Node( object ):
    def __init__( self, end_node = False ):
        self.end_node = end_node
        self.children = {}

class Trie( object ):
    
    """
    Create a trie to store list of strings with a word as a key.
    """
    def __init__( self ):
        self.root = Node()
    
    def insert( self, key ):
        """
        Split a string and store the prefix as the child of
        the root. 
        """
        current = self.root
        for k in key.split():
            # print k
            if k not in current.children:
                current.children[k] = Node()
            current = current.children[k]
        current.end_node = True
    
    def search( self, key ):
        """
        Search a word as a child of the root and return 
        pointer to the node.
        """
        current = self.root
        
        if key not in current.children:
            return False
        else:
            return current.children[key]

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

"""
The function removes colors from a sentence using trie class
which stores prefixes of colours.
Input: List of colors and sentence
Output: Sentence after removing colours
"""

colors = ['brown', 'maroon', 'multicolored', 'violet', 'navy', 'tan', 'light blue', 'cream', 'blue', 'peach', 'dark blue', 'purple', 'yellow', 'transparent', 'off white', 'black', 'orange', 'offwhite', 'red', 'pink', 'turquoise', 'khaki', 'off-white', 'white', 'multi', 'gunmetal', 'grey', 'multicolor', 'green', 'beige', 'light green', 'dark green','chocolate brown']

def searchPrefix(sentence):
    """
    Creates a trie from list of colors.
    Uses this trie to remove color names from sentence
    """
    db = Trie()
    for color in colors:
        db.insert(color)

    stringIndexed = sentence.lower().split()
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

# def main():
#     # string = "The jeans is light chocolate brown in color and has brown pockets"
#     string = sys.argv[1]
#     filteredString = searchPrefix(string.lower())
#     print filteredString
