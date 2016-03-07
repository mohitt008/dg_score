import sys
import os.path
import csv
from multiprocessing import Pool, cpu_count

PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname('__file__')))
sys.path.append(PARENT_DIR+"/../source/")

from Predict_Category.objects import categoryModel
from Predict_Category.predict_category import predict_category_tree

if __name__=="__main__":
    cat_model = categoryModel()
    reader = csv.reader(open("input.csv"))
    # Ignore keys
    reader.next()
    p = Pool(processes=cpu_count() - 2)
    f2 = open("output.csv", 'w')
    l = ['prd', 'cat', 'subcat']
    writer = csv.DictWriter(f2, fieldnames = l)
    writer.writeheader()

    # SK: TODO: cache (Redis) ...
    for row in reader:
        try:
            prd = row[1]
            res = p.apply_async(predict_category_tree,
                                args=(prd, cat_model,),)
            cat = res.get()[0]
            subcat = res.get()[1]
            result = {}
            result['prd'] = prd
            result['cat'] = cat
            result['subcat'] = subcat
            writer.writerow(result)
        except Exception as e:
            print e
            continue

    f2.close()
