import csv

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.products_db

reader = csv.reader(open('/home/delhivery/Downloads/category_list.csv', 'r'), delimiter=',')
for row in reader:
    if row[0]:
        print(row[0])
        category_id = db.categories.insert({'category_name': row[0], 'par_category': None})
        print(category_id)
    if row[1]:
        sub_cats = row[1].rstrip(';').split(';')
        for sub_cat in sub_cats:
            print(sub_cat)
            subcat_id = db.categories.insert({'category_name': sub_cat, 'par_category': ObjectId(category_id)})
            a = db.categories.update({"_id": ObjectId(category_id)},
                                     {'$addToSet': {'children': ObjectId(subcat_id)}},
                                     upsert=True)
            print(a)