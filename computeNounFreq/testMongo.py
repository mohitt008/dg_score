from pymongo import MongoClient

Client=MongoClient("mongodb://52.74.3.102:27017")
db=Client['snapdeal_test']
products=db['products']

print products.count()
