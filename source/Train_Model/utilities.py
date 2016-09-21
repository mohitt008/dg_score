__author__ = 'rohan'
import csv
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config.config_details import ROOT_PATH

def get_color_set():
    x=set()
    f=open(ROOT_PATH +'/data/colors.csv')
    reader=csv.reader(f)
    for row in reader:
        x.add(row[0].lower().strip())
    return x

def get_category_tree():
    category_tree={}
    f=open(ROOT_PATH+'/data/category_tree.csv')
    reader=csv.DictReader(f)
    for row in reader:
        if row.get('parent'):
            if category_tree.get(row.get('parent')):
                category_tree[row.get('parent')].append(row.get('category'))
            else:
                category_tree[row.get('parent')]=[row.get('category')]
        else:
            if not category_tree.get(row.get('category')):
                category_tree[row.get('category')]=[]
    return category_tree


COLOR_SET=get_color_set()
print get_category_tree()