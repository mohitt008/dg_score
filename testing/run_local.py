import sys
import os.path
import csv
from multiprocessing import Pool, cpu_count
import cProfile
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
l = ['prd', 'cat', 'subcat']
writer = csv.DictWriter(f2, fieldnames = l)
writer.writeheader()


def collect_results(res):
    #print "callback:", os.getpid()
    #print "callback:", res, type(res)
    result = {}
    result['prd'] = res[0]
    result['cat'] = res[1]
    result['subcat'] = res[2]
    writer.writerow(result)


"""
def wtf(prd):
    print os.getpid()
    print "worker", prd.upper()
    print "worker", type(cat_model)
"""


if __name__=="__main__":
    reader = csv.reader(open("input.csv"))
    # Ignore keys
    reader.next()
    p = Pool(processes = cpu_count() - 2)
    cnt = 0

    pr = cProfile.Profile()
    pr.enable()

    # SK: TODO: cache (Redis) ...
    for row in reader:
        try:
            prd = row[1].lower()
            p.apply_async(predict_category_tree,
                          args=(prd, ),
                          callback=collect_results)
            cnt += 1
            #print cnt
        except Exception as e:
            print e
            continue
    p.close()
    p.join()

    f2.close()

"""
    pr.disable()

    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
"""
