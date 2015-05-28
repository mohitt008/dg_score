client = MongoClient()
db = client["snapdeal"]
products = db["products"]

result = products.find({},{"product_category_id":1})
print result