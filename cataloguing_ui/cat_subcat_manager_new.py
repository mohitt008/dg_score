from config import db
from bson.objectid import ObjectId

cur = db.products.aggregate([{"$group": { "_id": { "vendor_cat":"$vendor_cat",
								"vendor_subcat":"$vendor_subcat", "vendor":"$vendor" } } }])

for combinations in cur:
	d = combinations["_id"]
	if d["vendor_cat"]:
		cat = db.categories.find_and_modify( query={"category_name":d["vendor_cat"], "par_category":None,
													"vendor":d["vendor"]},
												update={"$set":{"category_name":d["vendor_cat"], "par_category":None,
													"vendor":d["vendor"]}},
												upsert=True,
												new=True
												)
		if d["vendor_subcat"]:
			subcat = db.categories.find_and_modify( query={"category_name":d["vendor_subcat"],
														"par_category":ObjectId(cat["_id"]), "vendor":d["vendor"]},
														update={"$set":{"category_name":d["vendor_subcat"],
														"par_category":ObjectId(cat["_id"]), "vendor":d["vendor"]}},
														upsert=True,
														new=True
														)
			db.categories.update( {"_id":cat["_id"]}, {"$addToSet":{"children":ObjectId(subcat["_id"])}} )