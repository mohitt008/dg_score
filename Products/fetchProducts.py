from pymongo import MongoClient
import json
from bson import json_util
import sys
from math import sqrt
import random
from datetime import datetime
from database import dbInfo

client = MongoClient()
if dbInfo.database not in client.database_names():
	raise Exception("Database does not exists")
db = client[dbInfo.database]

if dbInfo.productTable not in db.collection_names():
	raise Exception("Collection {} does not exists".format(dbInfo.productTable))
products = db[dbInfo.productTable]

if dbInfo.categoryTable not in db.collection_names():
	raise Exception("Collection {} does not exists".format(dbInfo.productTable))
categories = db[dbInfo.categoryTable]

if dbInfo.channelCategoryTable not in db.collection_names():
	raise Exception("Collection {} does not exists".format(dbInfo.productTable))
catMapping = db[dbInfo.channelCategoryTable]

def getCategories(delhiveryCategory):

	"""
	Input: delhiveryCategory ID (int)
	Process: Fetch child categories for delhiveryCategory if present. For all those categories,
	get associated vendor category ID.
	Output: List of vendor category IDs
	"""
	if products.find({"delhivery_cat_id":delhiveryCategory}).count() == 0:
		raise Exception("Category does not exist")

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
	Input: Products available for the delhivery category in Database(productsAvail) (int),
		   Number of products requested by user(userLimit) (int)
	Process: Generate random numbers in the range 1 to number of products available 
	for the category. If number requested by user is less/equal to half of available products 
	then generate (userLimit) number of random numbers between 1 to productsAvail. Otherwise 
	generate (productsAvail - userLimit) number of random numbers from same range and reject 
	the numbers generated. 
	Output: List of random numbers
	"""
	if userLimit <= productsAvail/2:
		randomDocuments = random.sample(range(1,productsAvail+1),userLimit)
	else:
		randomList = random.sample(range(1,productsAvail+1),productsAvail - userLimit)
		randomDocuments = [val for val in range(1,productsAvail+1) if val not in randomList]
	return randomDocuments

def getProducts(delCategory,n):
	
	"""
	Input: Delhivery Category ID(int), count of products(int)
	Process: Invoke functions getCategories to obtain list of Vendor Category ID associated
	with the delhivery category ID and genRandom to generate n random numbers. getProducts 
	fetches the product details based on the sequence number generated from genRandom function
	and vendor categories.
	Output: Json containing Product information
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
	for key in finalList:
		values = list(finalList[key])
		docs = products.find({"product_category_id":key,"seq":{"$in":values}})
		for doc in docs:
			json_results.append(doc)

	return json.dumps(json_results, default=json_util.default, indent = 4)	


if __name__ == '__main__':
	delhivery_category = int(sys.argv[1])
	count = int(sys.argv[2])
	productInfo = getProducts(delhivery_category,count)