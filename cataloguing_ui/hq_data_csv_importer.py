import csv
import glob
import json

from pymongo import MongoClient
from category_service import request_to_segment_product
from prompt_cloud_importer import create_pool

client = MongoClient()
db = client.products_db

data = []

for files in glob.glob("data/hq_data/*.csv"):
    with open(files,'rt') as f:
        tempreader = csv.reader(f, delimiter=',')
        row_no = 0
        for row in tempreader:
            if row_no == 0:
                row_no = 1
                continue
            dict_name = {}
            dict_name["product_name"] = row[0]
            data.append(dict_name)

#print(data) 

end = len(data)           
print(end)

create_pool(data, 0, end, int(end/16))
