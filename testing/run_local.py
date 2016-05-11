import sys
import os.path
import csv

PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname('__file__')))
sys.path.append(PARENT_DIR + "/../source/")

from Predict_Category.predict_category import *
from Predict_Category.find_categories import predict_dg

f2 = open("output.csv", 'w')
l = ['prd', 'cat', 'subcat', 'cat_confidence', 'dg']
writer = csv.DictWriter(f2, fieldnames=l)
writer.writeheader()


def collect_results(res, prd, client_name):
    result = {}
    result['prd'] = prd
    result['cat'] = res[0]
    result['subcat'] = res[1]
    result['cat_confidence'] = res[2]
    dg_res = predict_dg(prd.lower(), res[0], None, None, client_name.lower())
    result['dg'] = dg_res['dangerous']
    writer.writerow(result)

if __name__ == "__main__":
    reader = csv.reader(open("prd.csv"))
    # Ignore keys
    reader.next()
    cnt = 0

    for row in reader:
        try:
           res = predict_category_tree(row[0])
           collect_results(res, row[0], row[1])

           cnt += 1
           # print cnt
           #if cnt > 50:
               #break
        except Exception as e:
            print e
            # continue
            break

    f2.close()
