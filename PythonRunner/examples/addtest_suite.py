from tesecase import TestAssertion1
from tesecase import TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

#this suite will run 'testcase.TestAssertion1.test_1','testcase.TestAssertion1.test_3','testcase.TestAssertion1.test_2',testcase.TestAssertion2.test_6',testcase.TestAssertion2.test_5'
def suite():
    tests=[TestAssertion1("test_1"),TestAssertion1("test_3"),TestAssertion1("test_2"),TestAssertion2("test_6"),TestAssertion2("test_5")]
    suites = unittest.TestSuite()
    suites.addTests(tests)
    return suites


if __name__ == '__main__':
    to_users = 'wgu@sonicwall.com'
    cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite(), to_users, cc_users)
    st.run()
