import os
import csv
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.products_db
tag_dict = {}


def get_code(word):
    word = word.capitalize()
    if word in tag_dict.keys():
        return tag_dict[word]
    for k in range(len(word)):
        code = word[:k+1]
        if code not in tag_dict.values():
            tag_dict[word] = code
            # print(tag_dict)
            return code
    print(tag_dict)


fn = os.path.join(os.path.dirname(__file__), 'data/category_attrs_mapping.csv')
reader = csv.reader(open(fn, 'r'), delimiter=',')
next(reader, None)
for row in reader:
    if row[0]:
        cat_obj = db.categories.find_and_modify(
            {"category_name": row[0]},
            {'$setOnInsert': {'par_category': None}},
            new=True,
            upsert=True
        )
        # print(cat_obj)

        tag_list = None
        if row[1]:
            tags = row[1].split(';')
            for tag in tags:
                tag_list = dict((tag.strip(), get_code(tag.strip())) for tag in tags)
            # print(tag_list)
            res = db.categories.update({'_id': ObjectId(cat_obj['_id'])},
                                       {'$set': {'tags': tag_list}})

    if row[2]:
        print(row[2])
        subcat_id = db.categories.insert({'category_name': row[2], 'par_category': ObjectId(cat_obj['_id'])})
        print(subcat_id)
        a = db.categories.update({"_id": ObjectId(cat_obj['_id'])},
                                 {'$addToSet': {'children': ObjectId(subcat_id)}},
                                 upsert=True)
        print(a)

        tag_list = None
        if row[3]:
            tags = row[3].split(';')
            for tag in tags:
                tag_list = dict((tag.strip(), get_code(tag.strip())) for tag in tags)
            # print(tag_list)
            res = db.categories.update({'_id': ObjectId(subcat_id)},
                                       {'$set': {'tags': tag_list}})
print(tag_dict)