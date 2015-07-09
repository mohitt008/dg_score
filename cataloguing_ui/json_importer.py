import json
from pymongo import MongoClient
from category_service import request_to_segment_product
client = MongoClient()
db = client.products_db

data = []
with open('/home/delhivery/Downloads/saquib.json') as f:
    for line in f:
        data.append(json.loads(line))

# print(data)
x = 0
name_list = []
for i in data:
    for j in i:
        x=x+1
        response = request_to_segment_product([{'product_name': j['record']['product_name']}])[0]
        print(j['record']['product_name'])
        print(response)
        if response['sub_category']:
            try:
                subcat = response['sub_category'].split('->')[1]
            except IndexError:
                subcat= response['sub_category'].split('->')[0]
        else:
            subcat = None
        db.products.insert({'product_name': j['record']['product_name'],
                            "vendor": 'Flipkart',
                            "category": response['category'],
                            "sub_category": subcat})

print('No of records: ', x)
