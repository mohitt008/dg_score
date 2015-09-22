import os
from constants import PARENT_DIR_PATH

sys.path.append(PARENT_DIR_PATH)

def create_model():
	dangerous_cat_set = set()
	f_dang = open(PARENT_DIR_PATH+"/dangerous_categories.csv")
	reader = csv.DictReader(f_dang)
	for row in reader:
	    if row['dang'] == "1":
	        dangerous_cat_set.add(row['cat_name'])
	f_dang.close()

	dangerous_word_set = set()
	f_dang = open(PARENT_DIR_PATH + "/dangerous_words.csv")
	reader = csv.reader(f_dang)
	for row in reader:
	    dangerous_word_set.add(row[0])
	f_dang.close()

	dangerous_ambi_set = set()
	f_dang = open(PARENT_DIR_PATH + "/dangerous_ambi.csv")
	reader = csv.reader(f_dang)
	for row in reader:
	    dangerous_ambi_set.add(row[0])
	f_dang.close()

	non_dangerous_set = set()
	f_dang = open(PARENT_DIR_PATH + "/non_dangerous_words.csv")
	reader = csv.reader(f_dang)
	for row in reader:
	    non_dangerous_set.add(row[0])
	f_dang.close()

	second_level_cat_names_set = set(second_level_cat_names)