from config import my_logger, sentry_client, db
from bson.objectid import ObjectId

def add_user(user_dict):
    my_logger.info("Inside add_user function with user_dict = {}".format(user_dict))

    to_retain = ['id', 'name', 'gender', 'email', 'link', 'user_type']
    data_dict = dict(map(lambda key: (key, user_dict.get(key, None)), to_retain))
    try:
        user_c = db.users.find({'id': data_dict['id']}).count()
        if user_c < 1:
            data_dict.update({'tags':0, 'tags_verified':0})
            my_logger.info("Adding new user with data = {}".format(data_dict))
            db.users.update({'id': data_dict['id']}, data_dict, upsert=True)
    except Exception as e:
        my_logger.error("Error in adding user = {}".format(str(e)))
        sentry_client.captureException(
            message = "Exception while adding user",
            extra = {"Exception": e}
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