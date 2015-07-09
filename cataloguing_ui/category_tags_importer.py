import csv

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.products_db
tag_dict = {}
#finding all existing codes
# # t = db.categories.find({'tags': {'$exists': True}}, {'tags': 1})
# # lis = []
# # for i in t:
# #     lis.append(i['tags'])
# s = set(val for dic in lis for val in dic.values())
# print(s)


def get_code(word):
    word = word.capitalize()
    if word in tag_dict.keys():
        return tag_dict[word]
    for k in range(len(word)):
        code = word[:k+1]
        if code not in tag_dict.values():
            tag_dict[word] = code
            print(tag_dict)
            return code
    print(tag_dict)
# print('code', get_code('And'))
# print('code', get_code('abdd'))
# print('code', get_code('Abd'))

reader = csv.reader(open('/home/delhivery/category_tags_mapping.csv', 'r'), delimiter=',')
for row in reader:
    tag_list = None
    if row[2]:
        tags = row[2].split(';')
        for tag in tags:
            tag_list = dict((tag, get_code(tag)) for tag in tags)
        # print(tag_list)

    if row[0]:
        cat_obj = db.categories.find_and_modify(
            {"category_name": row[0]},
            {'$setOnInsert': {'par_category': None}},
            new=True,
            upsert=True
        )
    if row[1]:
        subcat_id = db.categories.insert({'category_name': row[1], 'par_category': ObjectId(cat_obj['_id'])})
        # print(subcat_id)
        a = db.categories.update({"_id": ObjectId(cat_obj['_id'])},
                                 {'$addToSet': {'children': ObjectId(subcat_id)}})
        # print(a)
    if tag_list is not None:
        if row[1]:
            res = db.categories.update({'_id': ObjectId(subcat_id)},
                                       {'$set': {'tags': tag_list}})
        else:
            res = db.categories.update({'_id': ObjectId(cat_obj['_id'])},
                                       {'$set': {'tags': tag_list}})
        # print(res)