import pandas
import random
import csv



filename = "Final_flaseDG_training_data.csv"
"""
n = sum(1 for line in open(filename)) - 1 #number of records in file (excludes header)
x = 161511 #desired sample size

s= int(float(.5/.5)*(x))
skip = sorted(random.sample(xrange(1,n+1),n-s)) #the 0-indexed header will not be included in the skip list
df1 = pandas.read_csv(filename, skiprows=skip,error_bad_lines=False)
df2 = pandas.read_csv('Final_trueDG_training_data.csv')
df3 = pandas.concat([df1,df2])
df = df3[df3.dg.notnull()]
"""
"""data= zip(df['prd'],df['client'],df['cat'],df['subcat'],df['dg'])
writer = csv.writer(open('Final_training_data_50-50.csv','w'))
writer.writerow(['prd\tclient\tcat\tsubcat\tdg'])
for line in data:
	writer.writerow(line)
"""
"""
df.to_csv('Final_training_data_50-40.csv')
"""
n = sum(1 for line in open(filename)) - 1 #number of records in file (excludes header)
x = 161511 #desired sample size

s= int(float(.5/.5)*(x))
with open(filename, "rb") as source:
    lines = [line for line in source]

random_choice = random.sample(lines, s)

with open("Final_flaseDG_training_data_50-50.csv", "wb") as sink:
    sink.write("\n".join(random_choice))