import csv
s = csv.reader(open('classified_mongo_amazon_data.csv','rb'))
print s
next(s,None)
d = csv.writer(open('mongo_amazon_data.csv','wb'))
d.writerow(['prd','client','cat','subcat','cat_confidence','dg','dg_keyword','amazon_cat','amazon_subcat','amazon_sub_subcat','amazon_sub_sub_subcat'])
for row in s:
	x= row[7].split('---->')
	#print x
	result= row[:7]+x[:4]
	d.writerow(result)


