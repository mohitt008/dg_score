import csv
import glob

from prompt_cloud_importer import create_pool

data = []
for files in glob.glob("data/hq_data/*.csv"):
    with open(files,'rt') as f:
        tempreader = csv.reader(f, delimiter=',')
        next(tempreader, None)
        for row in tempreader:          
            data.append({'product_name': row[0]})

end = len(data)           
print(end)
create_pool(data, 0, end, int(end/16))
