from examples.testcase_skip_method import TestAssertion1
from runner.unittest.suite import UnittestSuite
import unittest
import sys

def suite():
    suites = unittest.TestLoader().loadTestsFromNames(['examples.testcase_skip_method.TestAssertion1'])
    return suites

if __name__ == '__main__':
    to_users = 'cliu@sonicwall.com'
    cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite(), to_users, cc_users)
    st.run()
