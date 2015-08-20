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
        data_dict.update({'tags':0, 'tags_verified':0})
        a = db.users.update({'id': data_dict['id']}, data_dict, upsert=True)
        print('update result...', a)
        return a
    else:
        return 0


def get_tag_count(user_id):
    tags = db.users.find_one({"id": user_id})
    return tags['tags'], tags['tags_verified'] if 'tags_verified' in tags else 0


def inc_tag_count(user_id, admin=False):
    if admin:
        db.users.update({'id': user_id}, {'$inc': {'tags_verified': 1}})
    else:
        db.users.update({'id': user_id}, {'$inc': {'tags': 1}})


def get_users():
    return db.users.find({},{'name':1, 'tags':1, 'tags_verified':1, 'email':1, 'id':1, '_id':0}).sort([('tags', -1)])