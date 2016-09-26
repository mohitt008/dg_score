import csv
import random as r


filename = "final_falseDG_data.csv"

f1 = open(filename)
f1_reader = csv.reader(f1)
f2 = open('New_Final_all_training_data.csv', 'w')
f2_writer = csv.writer(f2)

for row in f1_reader:
	result= row[:4]+[row[6]]
	f2_writer.writerow(result)
	break

for row in f1_reader:
	if (r.randrange(1,101)) < 100:
		result= row[:4]+[row[6]]
		f2_writer.writerow(result)

f3 = open("Final_trueDG_training_data.csv")
f3.next()
f3_reader = csv.reader(f3)

for row in f3_reader:
	f2_writer.writerow(row)

f4 = open("Result_mismatch_dg_ML_ruleEngine.csv")
f4.next()
f4_reader = csv.reader(f4)

for row in f4_reader:
	f2_writer.writerow(row)
f1.close()
f2.close()
f3.close()
f4.close()