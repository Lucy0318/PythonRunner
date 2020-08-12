from testcase import TestAssertion1
from testcase import TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

#this suite will run 'testcase.TestAssertion1.test_1','testcase.TestAssertion1.test_2','testcase.TestAssertion1.test_3','testcase.TestAssertion2.test_5','testcaseTestAssertion2.test_6'
def suite():
#    tests=['testcase.TestAssertion1.test_1','testcase.TestAssertion1.test_2','testcase.TestAssertion1.test_3','testcase.TestAssertion2.test_5','testcaseTestAssertion2.test_6']
    tests=['testcase.TestAssertion1','testcase.TestAssertion2']
    suites = unittest.TestLoader().loadTestsFromNames(tests)
    return suites


if __name__ == '__main__':
    st = UnittestSuite(sys.argv, suite())
    st.run()
