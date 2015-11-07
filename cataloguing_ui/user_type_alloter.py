from config import db, DELHIVERY, REVERSEGAZE, OTHERS

user_cur = db.users.find()

for user in user_cur:
	if not "user_type" in user:
		domain = user["email"].split('@')[1]
		if domain in DELHIVERY:
			db.users.update(user, {"$set":{"user_type":"delhivery"}})
		elif user["email"] in REVERSEGAZE:
			db.users.update(user, {"$set":{"user_type":"reversegaze"}})
		elif user['email'] in OTHERS:
			db.users.update(user, {"$set":{"user_type":"others"}})
