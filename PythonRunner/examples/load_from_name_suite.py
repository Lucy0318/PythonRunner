from testcase import TestAssertion1
from testcase import TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

#this suite will run 'testcase.TestAssertion1.test_1','testcase.TestAssertion1.test_2','testcase.TestAssertion1.test_3'
def suite():
#    tests=['testcase.TestAssertion1.test_1','testcase.TestAssertion1.test_2','testcase.TestAssertion1.test_3','testcase.TestAssertion2.test_5','testcaseTestAssertion2.test_6']
#    suites = unittest.TestLoader().loadTestsFromName('testcase.TestAssertion1.test_2')
    suites = unittest.TestLoader().loadTestsFromName('testcase.TestAssertion1')
    return suites


if __name__ == '__main__':
    # to_users = 'wgu@sonicwall.com'
    # cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite())
    st.run()
