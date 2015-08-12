''' 
Imports data from category_attrs_mapping.csv file (present in data folder) into mongodb
'''

import os
import csv
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.products_db

tag_dict = {}
tag_dict_obj = db.categories.distinct('tags')
for dicts in tag_dict_obj:
    tag_dict.update(dicts)
print(tag_dict)

def get_code(word):
    if word in tag_dict.keys():
        tag_dict[word] = tag_dict[word].capitalize()
        return tag_dict[word]
    for k in range(len(word)):
        code = word[:k+1]
        if code not in tag_dict.values():
            code = code.capitalize()
            tag_dict[word] = code
            # print(tag_dict)
            return code
    #print(tag_dict)


fn = os.path.join(os.path.dirname(__file__), 'data/category_attrs_mapping.csv')
reader = csv.reader(open(fn, 'r'), delimiter=',')
next(reader, None)
for row in reader:
    if row[0]:
        cat_obj = db.categories.find_and_modify(
            {"category_name": row[0]},
            {'$setOnInsert': {'par_category': None}},
            new = True,
            upsert = True
        )
        # print(cat_obj)

        tag_list = {}
        tag_list_obj = db.categories.find({"category_name": row[0]}).distinct('tags')
        for dicts in tag_list_obj:
            tag_list.update(dicts)
        #print(tag_list)
        if row[1]:
            tags = row[1].rstrip(';').split(';')
            for tag in tags:
                tag_list[tag.strip()] = get_code(tag.strip())
            #print(tag_list)
            res = db.categories.update({'_id': ObjectId(cat_obj['_id'])},
                                       {'$set': {'tags': tag_list}})

    if row[2]:
        #print(row[2])
        subcat_obj = db.categories.find_and_modify(
            {"category_name": row[2]},
            {'$setOnInsert':{'par_category': ObjectId(cat_obj['_id'])}},
            new = True,
            upsert = True
        )
        # print(subcat_id)
        a = db.categories.update({"_id": ObjectId(cat_obj['_id'])},
                                 {'$addToSet': {'children': ObjectId(subcat_obj['_id'])}})
        # print(a)

        tag_list = {}
        tag_list_obj = db.categories.find({"category_name": row[2]}).distinct('tags')
        for dicts in tag_list_obj:
            tag_list.update(dicts)
        #print(tag_list)
        if row[3]:
            tags = row[3].rstrip(';').split(';')
            for tag in tags:
                tag_list[tag.strip()] = get_code(tag.strip())
            #print(tag_list)
            res = db.categories.update({'_id': ObjectId(subcat_obj['_id'])},
                                       {'$set': {'tags': tag_list}})
print(tag_dict)