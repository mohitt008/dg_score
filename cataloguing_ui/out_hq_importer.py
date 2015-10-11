import csv

from pymongo import MongoClient
from prompt_cloud_importer import create_pool

client = MongoClient()
db = client.products_db

prod_list = []
with open("data/outsource_data/hq-data/wbn_prd_3month.csv",'rt') as f:
	tempreader = csv.reader(f, delimiter=',')
	next(tempreader, None)
	for row in tempreader:
		prod_list.append(row[2]+'$$@@$$'+row[1])

print(len(prod_list))
unique_list = list(set(prod_list))
print(len(unique_list))

data = []
for prod in unique_list:
	temp_list = prod.split('$$@@$$')
	data.append({'product_name': temp_list[0], 'retail_price': temp_list[1]})

end = len(data)           
print(end)
create_pool(data, 0, end, int(end/16))