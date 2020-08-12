from examples.subtest import TestAssertion1
from runner.unittest.suite import UnittestSuite
from runner.unittest.setup import NumbersTestResult
import unittest
import sys

def suite():
    test_cases = [TestAssertion1()]
    suites = unittest.TestSuite()
    i = 0
    while i < test_cases.__len__():
        suites.addTest(test_cases[i])
        i += 1
    return suites


if __name__ == '__main__':
#    runner = UnittestSuite.TextTestRunner(verbosity=2, resultclass=NumbersTestResult)
    # to_users = 'wgu@sonicwall.com'
    # cc_users = 'automation, shanghai_automation'
    runner = UnittestSuite(sys.argv, suite(), resultclass=NumbersTestResult)
    runner.run()

