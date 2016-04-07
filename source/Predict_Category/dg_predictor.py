#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
New/Improved DG detection logic:
Refer the document for complete details. The document is shared here:
https://goo.gl/hFtlXr

Usage:
from dg_predictor import DGPredictor
predictor = DGPredictor(
    product_name,   # String
    category,       # String
    dg_keywords     # list of rows of DG keywords file
)
dg_report = predictor.predict()  # return type: dictionary
print dg_report['dangerous']
print dg_report['prohibited']
"""

from settings import sentry_client
from objects import dangerousModel
import sys


try:
    dg_model = dangerousModel()
except Exception as e:
    sentry_client.captureException(
        message="dg_predictor: Failed to load dg model",
        extra={"error": e}
    )
    print "dg_predictor: Failed to load dg model"
    sys.exit()


class DGPredictor(object):
    """
    Determines whether a product is dangerous or prohibited by using a
    pre-defined set of potentially dangerous/prohibited keywords and a set
    of rules.
    """
    def __init__(self, product_name, category, logger=None):
        """
        All inputs are expected in lower case for
        string/sub-string matching.
        """
        self.product_name = product_name
        self.category = category
        self.logger = logger
        self.keyword = ""
        self.found_keyword = ""
        self.contain_list = ""
        self.contain_category = ""
        self.except_list = ""
        self.except_category = ""

    def __contains_category(self, haystack):
        """
        Finds if identified category of a product is there in a list of
        defined categories in either contain or except set.
        Input: haystack, list of contain or except categories
        Output: True/False
        """
        if len(haystack):
            return self.category in haystack.split(", ")
        else:
            return False

    def __contains_keyword(self, haystack):
        """
        Finds if any keyword from the contain or except list is there in the
        product name.
        Input: haystack, list of contain or except keywords
        Output: True/False
        """
        result = False
        if len(haystack):
            for contain_word in haystack.split(", "):
                if contain_word in self.product_name:
                    self.keyword = contain_word
                    result = True
                    break
        return result

    def __check_dg_false(self, rule):
        """
        If DG is false by default, we check if both contain list and contain
        category are there in the rules, if yes, the DG will be True if found
        in both contain list AND contain category. Otherwise, the result will
        be determined on OR value.
        """
        contain_list = rule[2]
        contain_category = rule[3]
        in_contain_list = self.__contains_keyword(contain_list)
        if in_contain_list:
            self.contain_list = self.keyword
        in_contain_category = self.__contains_category(contain_category)
        if in_contain_category:
            self.contain_category = self.category
        dg = False
        if len(contain_list) and len(contain_category):
            dg = in_contain_list and in_contain_category
        else:
            dg = in_contain_list or in_contain_category
        # If DG comes out to be true, go to DG = True workflow to
        # detetrmine final result.
        if dg:
            dg = self.__check_dg_true(rule)
        return dg

    def __check_dg_true(self, rule):
        """
        If DG is true by default then final outcome is simply a OR value of
        search in except list as well as except category.
        """
        except_list = rule[4]
        except_category = rule[5]
        in_except_list = self.__contains_keyword(except_list)
        if in_except_list:
            self.except_list = self.keyword
        in_except_category = self.__contains_category(except_category)
        if in_except_category:
            self.except_category = self.category
        return not (in_except_list or in_except_category)

    def __check_prohibited(self, rule):
        """
        If prohibited by default, we check if any keyword of except list is
        found in product name OR identified category is found in list of except
        categories. If yes, prohibited is false and we go to DG = True workflow
        to determine final DG result. If no, both DG and prohibited are True.
        """
        dg = prohibited = False
        except_list = rule[4]
        except_category = rule[5]
        in_except_list = self.__contains_keyword(except_list)
        if in_except_list:
            self.except_list = self.keyword
        in_except_category = self.__contains_category(except_category)
        if in_except_category:
            self.except_category = self.category
        found_in_except = in_except_list or in_except_category
        if found_in_except:
            dg = self.__check_dg_true(rule)
            prohibited = False
        else:
            dg = prohibited = True
        return (dg, prohibited)

    def predict(self, wbn = None):
        """
        Iterates over all DG/prohibited keywords defined in DG keywords file.
        Determines DG or prohibited value of a product name.
        Returns a dictionary containing dangerous and prohibited keys and
        True/False values.
        """
        dg = prohibited = False

        for rule in dg_model.dg_keywords:
            try:
                default = int(rule[0])
                keyword = str(rule[1])
                if keyword in self.product_name:
                    self.found_keyword = keyword
                    if default == 0:
                        dg = self.__check_dg_false(rule)
                        # If a non-DG product becomes DG for any keyword, then
                        # its a DG and break it right here.
                        if dg:
                            break
                    elif default == 1:
                        dg = self.__check_dg_true(rule)
                    elif default == 2:
                        (dg, prohibited) = self.__check_prohibited(rule)
                    else:
                        # Still check other rules, handle such cases at the
                        # time of sanitization of DG keywords file.
                        pass
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        'dg_predictor:Exception {} occurred against rule: {} \
                        for product {}'.format(e, rule, self.product_name)
                    )
                sentry_client.captureException(
                    message="dg_predictor:Exception occurred against rule",
                    extra={
                        "error": e,
                        "rule": rule,
                        "product_name": self.product_name
                    }
                )
                pass

        dg_report = {}
        dg_report['name'] = self.product_name
        dg_report["wbn"] = wbn
        dg_report['keyword'] = self.found_keyword
        dg_report['dangerous'] = dg
        dg_report['prohibited'] = prohibited
        dg_report['contain_list'] = self.contain_list
        dg_report['contain_category'] = self.contain_category
        dg_report['except_list'] = self.except_list
        dg_report['except_category'] = self.except_category

        if self.logger:
            self.logger.info('Check DG: Product Name: {} Report: {}'.format(
                    self.product_name,
                    dg_report
                )
            )
        return dg_report


def main():
    pass


if __name__ == '__main__':
    main()
