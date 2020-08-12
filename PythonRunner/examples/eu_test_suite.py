from examples.eu_test import TestEmailUtilInit
from runner.unittest.suite import UnittestSuite
import unittest
import sys

def suite():
    test_cases = [TestEmailUtilInit()]
    suites = unittest.TestSuite()
    i = 0
    while i < test_cases.__len__():
        suites.addTest(test_cases[i])
        i += 1
    return suites


if __name__ == '__main__':
    # to_users = 'cliu@sonicwall.com'
    # cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite())
    st.run()
