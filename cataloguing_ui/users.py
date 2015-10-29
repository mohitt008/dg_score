import config

from config import my_logger, sentry_client
from pymongo import MongoClient
from bson.objectid import ObjectId

try:
    client = MongoClient(config.MONGO_IP, 27017)
    db = client.products_db
    db.products.find().limit(1)
except Exception as e:
    my_logger.error("MongoClient Exception in users.py = {}".format(e))
    sentry_client.captureException(
        message = "MongoClient Exception in users.py",
        extra = {"Exception":e}
        )

def add_user(user_dict):
    my_logger.info("Inside add_user function")
    to_retain = ['id', 'name', 'gender', 'email', 'link']
    my_logger.info("User dict = {}".format(user_dict))
    data_dict = {}
    for key in to_retain:
        if key in user_dict:
            data_dict[key] = user_dict[key]
    my_logger.info("Data dict = {}".format(data_dict))
    try:
        user_c = db.users.find({'id': data_dict['id']}).count()
        my_logger.info("User successfully added")
        if user_c < 1:
            data_dict.update({'tags':0, 'tags_verified':0})
            a = db.users.update({'id': data_dict['id']}, data_dict, upsert=True)
            my_logger.info("Update result = {}".format(a))
            return a
        else:
            return 0
    except Exception as e:
        my_logger.error("Error in adding user = {}".format(str(e)))
        sentry_client.captureException(
            message = "Exception while adding user",
            extra = {"Exception":e}
            )


def get_tag_count(user_id):
    tags = db.users.find_one({"id": user_id})
    return tags['tags'], tags['tags_verified']


def inc_tag_count(user_id, admin=False):
    if admin:
        db.users.update({'id': user_id}, {'$inc': {'tags_verified': 1}})
    else:
        db.users.update({'id': user_id}, {'$inc': {'tags': 1}})


def dcr_tag_count(user_id, admin=False):
    if admin:
        db.users.update({'id': user_id}, {'$inc': {'tags_verified': -1}})
    else:
        db.users.update({'id': user_id}, {'$inc': {'tags': -1}})    


def get_users():
    return db.users.find({},{'name':1, 'tags':1, 'tags_verified':1, 'email':1, 'id':1, '_id':0}).sort([('tags', -1)])


def find_user(id):
    found_user = db.users.find_one({'id':id})
    return found_user['name']