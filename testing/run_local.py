import sys
import os.path
import csv
# from multiprocessing import Pool, cpu_count
# from functools import partial
#import cProfile
#import pstats
#import StringIO

PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname('__file__')))
sys.path.append(PARENT_DIR+"/../source/")

#from Predict_Category.objects import categoryModel
#from Predict_Category.predict_category import predict_category_tree
from Predict_Category.predict_category import *

#output = []
#cat_model = categoryModel()
f2 = open("output.csv", 'w')
l = ['prd', 'cat', 'subcat', 'cat_confidence']
writer = csv.DictWriter(f2, fieldnames = l)
writer.writeheader()


def collect_results(res, prd):
    #print "callback:", os.getpid()
    #print "callback:", res, type(res)
    print res
    result = {}
    result['prd'] = prd
    result['cat'] = res[0]
    result['subcat'] = res[1]
    result['cat_confidence'] = res[2]
    writer.writerow(result)

if __name__=="__main__":
    reader = csv.reader(open("input.csv"))
    # Ignore keys
    reader.next()
    # p = Pool(processes = cpu_count() - 2)
    cnt = 0

    #pr = cProfile.Profile()
    #pr.enable()

    # SK: TODO: cache (Redis) ...
    for row in reader:
        try:
            """
            SK: Disabled multiprocessing (issues with tensor flow)
            prd = row[1].lower()
            custom_callback = partial(collect_results,
                                      prd = prd)
            p.apply_async(predict_category_tree,
                          args=(prd, ),
                          callback=custom_callback)
            """
            res = predict_category_tree_using_cnn(row[1])
            collect_results(res, row[1])

            cnt += 1
            #print cnt
            if cnt > 50:
                break
        except Exception as e:
            print e
            # continue
            break
    #p.close()
    #p.join()

    f2.close()

