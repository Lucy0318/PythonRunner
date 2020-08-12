import testcase
#from testcase import TestAssertion1
#from testcase import TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

#will run TestAssertion1.test_1,TestAssertion1.test_2,TestAssertion1.test_3,TestAssertion2.test_5,TestAssertion2.test_6
def suite():
    tests='TestAssertion1'
    suites=unittest.TestLoader().loadTestsFromModule(testcase)
    return suites


if __name__ == '__main__':
    # to_users = 'wgu@sonicwall.com'
    # cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite())
    st.run()
