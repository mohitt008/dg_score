#!/usr/bin/env python
"""
Create a trie to store list of strings with a word as a key.
""" 
class Node( object ):
	def __init__( self, end_node = False ):
		self.end_node = end_node
		self.children = {}

class Trie( object ):
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