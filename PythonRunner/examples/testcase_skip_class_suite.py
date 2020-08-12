#from examples.testcase_skip_class import TestAssertion1,TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

def suite():
    suites = unittest.TestLoader().loadTestsFromNames(['examples.testcase_skip_class.TestAssertion1','examples.testcase_skip_class.TestAssertion2'])
    return suites

if __name__ == '__main__':
    to_users = 'cliu@sonicwall.com'
    cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite(), to_users, cc_users)
    st.run()
