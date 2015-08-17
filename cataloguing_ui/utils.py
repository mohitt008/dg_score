import re
import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from random import randint
from bson import json_util

client = MongoClient()
db = client.products_db


def segment_product(prod_name):
    prod_name = str(prod_name).replace(" ,", ",")
    prod_name = str(prod_name).replace(",", ", ")
    prod_name = str(prod_name).replace(",", ", ")
    prod_name = str(prod_name).replace(".", ". ")
    prod_name = str(prod_name).replace("-", " - ")
    prod_name = str(prod_name).replace("^", "^ ")
    prod_name = str(prod_name).replace("(", " ( ")
    prod_name = str(prod_name).replace(")", " ) ")
    prod_name = str(prod_name).replace("\n", " ")
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
    return db.categories.find({'par_category': None})


def get_subcategories(cat_id):
    cursor = db.categories.find({'par_category': ObjectId(cat_id)}, {'par_category': 0})
    json_results = []
    for result in cursor:
        json_results.append(result)
    return to_json(json_results)


def get_vendors():
    return db.products.distinct('vendor')


def get_taglist(cat_name):
    cat_obj = db.categories.find_one({"category_name": cat_name})
    print(cat_obj)
    if cat_obj is not None and 'tags' in cat_obj:
        return cat_obj['tags']
    else:
        return {}


def get_all_tags():
    tags_cursor = db.categories.find({'tags': {'$exists': True}}, {'_id': 0, 'tags': 1})
    tags = {}
    for tag_dict in tags_cursor:
        tags.update(tag_dict['tags'])
    print('######tag list######', tags, type(tags))
    return tags


def get_product_tagging_details(query, to_verify=False):
    product = get_random_product(query, to_verify)
    if product is not None:
        prod_seg = segment_product(product['product_name'])
        print('###product segmentation###')
        print(prod_seg)
        tag_list = get_taglist(product['category'])
        tag_list.update(get_taglist(product['sub_category']))

        tag_info = {}
        tag_info['id'] = str(product['_id'])
        tag_info['prod_name'] = product['product_name']
        tag_info['vendor'] = product['vendor']
        tag_info['prod_cat'] = product['category']
        tag_info['prod_subcat'] = product['sub_category']
        tag_info['prod_url'] = product['product_url']
        tag_info['taglist'] = tag_list
        tag_info['prod_seg'] = json.dumps(prod_seg)

        if to_verify:
            tag_info['tags'] = product['tags']
            tag_info['is_dang'] = product['is_dang']
            tag_info['is_xray'] = product['is_xray']
            tag_info['is_dirty'] = product['is_dirty']

        return tag_info
    else:
        return json.dumps({'error': 'No untagged products for this vendor.'})


def update_category(id, cat, subcat):
    res = db.products.update({'_id': ObjectId(id)}, {"$set": {"category": cat,
                                                              "sub_category": subcat}
    })
    if res['updatedExisting']:
        return json.dumps({'message': 'Category Added Successfully.'})
    else:
        return json.dumps({'message': 'Error!'})


def get_random_product(query, to_verify=False):
    if to_verify:
        query['tags'] = {'$exists': True}
        query['verified'] = {'$exists': False}
    else:
        query['done'] = {'$exists': False}
        query['is_dirty'] = {'$exists': False}

    untagged_count = db.products.find(query).count()
    rand_no = randint(0, untagged_count)
    cur = db.products.find(query).limit(-1).skip(rand_no)
    prod_obj = next(cur, None)
    print('random product name object:', prod_obj)
    return prod_obj


def get_skip_count(product_id):
    temp_dict = db.products.find({"_id":ObjectId(product_id)},{"skip_count":1,"_id":0})
    for items in temp_dict:
        if 'skip_count' in items:
            return int(items["skip_count"])
        return 0