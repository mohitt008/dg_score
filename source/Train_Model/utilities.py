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

COLOR_SET=get_color_set()
