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
    """
    Class Node serves as a struture to trie.
    """
    def __init__( self, end_node = False ):
        self.end_node = end_node
        self.children = {}

class Trie( object ):

    """
    Create a trie to store list of strings with a word as a key and
    with the root having end_node as False and children empty
    Example: colors = ["chocolate brown","brown"]
    During insert, chocolate brown splits into chocolate becomes child
    to root, it's end_node as False and brown becomes and child to chocolate
    with end_node as True. Next element brown becomes a child to root with
    end_node as False and children empty

                        --------------
                         root | False
                        --------------
                        /            \
                       /              \
            ------------------    ------------------
            chocolate | False        brown | True
            ------------------    ------------------
                   /
                  /
        ------------------
           brown | True
        ------------------

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


def searchPrefix(sentence,db):
    """
    The function removes colors from a sentence using trie class which stores prefixes of colours.
    Input: Sentence as a list of tokens
    Output: List after removing colours
    """
    print db.root.children
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

    if stringIndexed:
        return stringIndexed
    else:
        return ['']

db = Trie()
fp =  open("colorList.txt","rb")
for line in fp:
    db.insert(line.strip())



