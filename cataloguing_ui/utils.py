import re
import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from random import randint
from bson import json_util
from category_service import request_to_segment_product

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


def get_product_tagging_details(query):
    product = get_random_product(query)
    if product is not None:
        prod_seg = segment_product(product['product_name'])
        print(prod_seg)
        tag_info = []
        tag_info.append({
            'id': str(product['_id']),
            'prod_name': product['product_name'],
            'prod_cat': product['category'],
            'prod_subcat': product['sub_category'],
            'prod_seg': json.dumps(prod_seg)
        })
        print(tag_info)
        return tag_info[0]
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


def get_random_product(query):
    query['tag'] = {'$exists': False}
    untagged_count = db.products.find(query).count()
    rand_no = randint(0, untagged_count)
    cur = db.products.find(query).limit(-1).skip(rand_no)
    prod_obj = next(cur, None)
    print('random product name object:', prod_obj)
    return prod_obj