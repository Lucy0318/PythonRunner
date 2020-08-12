from testcase import TestAssertion1
from testcase import TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

def suite():
    tests='TestAssertion1'
    suites=unittest.TestLoader().loadTestsFromTestCase(TestAssertion1)
    return suites


if __name__ == '__main__':
    # to_users = 'wgu@sonicwall.com'
    # cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite())
    st.run()
