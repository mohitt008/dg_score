import re
import json

from config import my_logger, sentry_client, db
from bson.objectid import ObjectId
from random import randint
from bson import json_util
from users import find_user

def segment_product(prod_name):
    prod_name = str(prod_name).replace(" ,", ",").replace(", ", ",").replace(",", " , ")\
                                .replace(".", " . ").replace("-", " - ").replace("^", " ^ ")\
                                .replace("+", " + ").replace("(", " ( ").replace(")", " ) ")\
                                .replace("|", " | ").replace(":", " : ").replace(";", " ; ").replace("\n", " ")
    prod_name = re.sub("[\s]+", " ", prod_name)
    prod_name = str(prod_name).strip()
    segmented_array = str(prod_name).split(" ")
    new_segments = list()
    for data_segment in segmented_array:
        segments = re.findall("[0-9]{*}[A-Z]{2,}[0-9]{*}|[0-9]{*}[A-Z][a-z]+[0-9]{*}|[0-9]{*}[a-z]+[0-9]{*}",
                              data_segment)
        if len(segments) > 0:
            new_segments += segments
        else:
            new_segments.append(data_segment)
    # print(new_segments)
    return new_segments


def to_json(data):
    """Convert Mongo object(s) to JSON"""
    return json.dumps(data, default=json_util.default)


def get_categories():
    return db.categories.find({'par_category': None}).sort([('category_name', 1)])


def get_subcategories(cat_id):
    try:
        cursor = db.categories.find({'par_category': ObjectId(cat_id)},
                                    {'par_category': 0}).sort([('category_name', 1)])

        json_results = []
        for result in cursor:
            json_results.append(result)
        my_logger.info("Result for get sub-categories = {}".format(json_results))
        return to_json(json_results)
    except Exception as e:
        my_logger.error("Exception in get_subcategories function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in get_subcategories function",
            extra = {"Exception": e}
            )


def get_vendors():
    return db.products.distinct('vendor')


def get_taglist(cat_name):
    cat_obj = db.categories.find_one({"category_name": cat_name})
    my_logger.info("Tag-list object for the category {} : {}".format(cat_name, cat_obj))
    if cat_obj is not None and 'tags' in cat_obj:
        return cat_obj['tags']
    else:
        return {}


def get_all_tags():
    tags_cursor = db.categories.find({'tags': {'$exists': True}}, {'_id': 0, 'tags': 1})
    tags = {}
    for tag_dict in tags_cursor:
        tags.update(tag_dict['tags'])
    my_logger.info("In get_all_tags function, tags = {}, type of tags = {}".format(tags, type(tags)))
    return tags


def get_product_tagging_details(query, to_verify=False, skipped_thrice=False):
    my_logger.info("Inside get_product_tagging_details function with query = {}".format(query))
    tag_info = {}
    if '_id' in query:
        product = db.products.find_one(query)
        if 'admin_tags' in product:
            tag_info['tags'] = product['admin_tags']
        else:
            tag_info['tags'] = product['tags'] if 'tags' in product else None
        tag_info['is_dirty'] = product['is_dirty'] if 'is_dirty' in product else None
    else:
        product = get_random_product(query, to_verify, skipped_thrice)

    if product is not None:
        prod_seg = segment_product(product['product_name'])
        my_logger.info("Fetched product segmentation = {}".format(prod_seg))
        tag_list = get_taglist(product['category'])
        tag_list.update(get_taglist(product['sub_category']))
        
        tag_info['id'] = str(product['_id'])
        tag_info['prod_name'] = product['product_name']
        tag_info['vendor'] = product['vendor']
        tag_info['prod_cat'] = product['category']
        tag_info['prod_subcat'] = product['sub_category']
        tag_info['prod_url'] = product['product_url']
        tag_info['price'] = product['price']
        tag_info['taglist'] = tag_list
        tag_info['prod_seg'] = json.dumps(prod_seg)

        if to_verify:
            if 'admin_tags' in product:
                tag_info['tags'] = product['admin_tags']
            else:
                tag_info['tags'] = product['tags']
            tag_info['is_dirty'] = product['is_dirty']
            found_user = find_user(product['tagged_by'])
            tag_info['tagged_by'] = found_user+" - "+product['tagged_by']

        return tag_info
    else:
        return {'error': 'No untagged products for this vendor.'}


def add_new_subcat( cat_id, subcat ):
    my_logger.info("Inside add_new_subcat function with cat_id = {} and subcat = {}".format(cat_id, subcat))
    category_id = ObjectId(cat_id)
    subcat = subcat.title()
    subcat_id = db.categories.insert({'category_name':subcat, 'par_category':category_id})
    db.categories.update({'_id':category_id}, {'$addToSet':{'children':ObjectId(subcat_id)}})
    return 'Added'


def update_category(id, cat, subcat):
    my_logger.info("Inside update_category function with id = {}, cat = {} and subcat = {}".format(id, cat, subcat))
    res = db.products.update({'_id': ObjectId(id)}, {"$set": {"category": cat,
                                                              "sub_category": subcat}
    })
    if res['updatedExisting']:
        return json.dumps({'message': 'Category Added Successfully.'})
    else:
        return json.dumps({'message': 'Error!'})


def get_random_product(query, to_verify=False, skipped_thrice=False):
    if to_verify:
        query['tags'] = {'$exists': True}
        query['verified'] = {'$exists': False}
    elif skipped_thrice:
        query['verified'] = {'$exists': False}
        query['skip_count'] = {'$exists': True, '$gt': 2}
    else:
        query['tagged_by'] = {'$exists': False}
        query['$or'] = [{'skip_count': {'$exists': False}}, {'skip_count': {'$lt': 3}}]

    untagged_count = db.products.find(query).count()
    rand_no = randint(0, untagged_count)
    cur = db.products.find(query).limit(-1).skip(rand_no)
    prod_obj = next(cur, None)
    #print("------------------Random product name object------------------")
    #print(prod_obj)
    my_logger.info("Random product name object = {}".format(prod_obj))
    return prod_obj


def inc_skip_count(product_id):
    db.products.update({'_id':ObjectId(product_id)},{'$inc':{'skip_count':1}})
