from pymongo import MongoClient
import json
from bson import json_util
import sys
from math import sqrt
import random
from datetime import datetime
from database import dbInfo

client = MongoClient()
db = client[dbInfo.database]
products = db[dbInfo.productTable]
categories = db[dbInfo.categoryTable]
catMapping = db[dbInfo.channelCategoryTable]

def getCategories(delhiveryCategory):

	"""
	Get delhivery categories with the given user category as parent
	"""
	if products.find({"delhivery_cat_id":delhiveryCategory}).count() == 0:
		print "Category {} does not exist".format(delhiveryCategory)
		sys.exit(0)

	categoryList = []
	categoryList.append(delhiveryCategory)
	childCategories = categories.find({"Category_Parent":delhiveryCategory})
	for childCategory in childCategories:
		categoryList.append(childCategory["Category_Id"])
	
	## Get list of categories from vendor partners associated with the delhivery categories
	vendorCategory = {}
	countProducts = 0
	vendorCategories = catMapping.find({"Category_Id" :{"$in" : categoryList}})

	for vc in vendorCategories:
		vendorCategory[vc["Channel_Category_Id"]] = vc["count"]
		countProducts = countProducts + vc["count"]

	vendorCategory = [(a,vendorCategory[a]) for a in vendorCategory]

	return vendorCategory,countProducts

def genRandom(productsAvail,userLimit):

	"""
	Generate random numbers in the range 1 to number of products 
	available for the category.
	"""
	if userLimit <= productsAvail/2:
		randomDocuments = random.sample(range(1,productsAvail+1),userLimit)
	else:
		randomList = random.sample(range(1,productsAvail+1),productsAvail - userLimit)
		randomDocuments = [val for val in range(1,productsAvail+1) if val not in randomList]
	return randomDocuments

def getProducts(delCategory,n,channel_cat):
	
	"""
	invoke functions getCategories and genRandom and
	fetch product details based on the sequence number
	generated from genRandom function
	"""
	vendorCategoryList,productCount = getCategories(delCategory)
	
	if n > productCount:
		## Limit exceeded count of products available
		n = productCount

	documentList  = genRandom(productCount,n)
	
	finalList = {}
	for document in documentList:
		temp = document
		for key,value in vendorCategoryList:
			if value >= temp: 
				if key not in finalList:
					finalList[key] = set()
				finalList[key].add(temp)
				break
			else:
				temp = temp - value

	json_results = []
	print finalList
	for key in finalList:
		values = list(finalList[key])
		docs = products.find({"product_category_id":key,"seq":{"$in":values}})
		for doc in docs:
			json_results.append(doc)

	# print json_results
	print json.dumps(json_results, default=json_util.default, indent = 4)	


if __name__ == '__main__':
	delhivery_category = int(sys.argv[1])
	count = int(sys.argv[2])
	vendor_category = -1
	if(len(sys.argv) == 4):
		vendor_category = int(sys.argv[3])
	getProducts(delhivery_category,count,vendor_category)