'''
Imports the data in HQSUBCAT.csv (located in data folder) into MongoDb
'''

import csv
from pymongo import MongoClient
client = MongoClient()
db = client.products_db

data = []
bulk = db.products.initialize_ordered_bulk_op()
with open('data/HQSUBCAT.csv','rt') as f:
	tempreader = csv.reader(f, delimiter=',')
	next(tempreader, None)
	for row in tempreader:
		if row[1] and row[2] and row[1] not in data:
				data.append(row[1])
				bulk.insert({'product_name':row[1], 'vendor':'HQSUBCAT',
									'category':row[2], 'sub_category': None, 'product_url': None})

bulk.execute()
print(len(data))