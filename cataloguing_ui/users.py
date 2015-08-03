from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.products_db


def add_user(user_dict):
    '''
    Adds a user to the users dict
    '''
    to_retain = ['id', 'name', 'gender', 'email', 'link']
    print(user_dict)
    data_dict = {}
    for key in to_retain:
        if key in user_dict:
            data_dict[key] = user_dict[key]
    print(data_dict)
    user_c = db.users.find({'id': data_dict['id']}).count()
    if user_c < 1:
        data_dict.update({'tags': 0})
        a = db.users.update({'id': data_dict['id']}, data_dict, upsert=True)
        print('update result...', a)
        return a
    else:
        return 0


def get_tag_count(user_id):
    return db.users.find_one({"id" : user_id})['tags']


def inc_tag_count(user_id):
    db.users.update({'id': user_id}, {'$inc': {'tags': 1}})


def get_users():
    return db.users.find({},{'name':1, 'tags':1, '_id':0}).sort([('tags', -1)])

def inc_skip_count(product_id):
    db.products.update({"_id":ObjectId(product_id)},{"$inc":{"skip_count":1}})

def get_skip_count(product_id):
    temp_dict = db.products.find({"_id":ObjectId(product_id)},{"skip_count":1,"_id":0})
    for items in temp_dict:
        return int(items["skip_count"])