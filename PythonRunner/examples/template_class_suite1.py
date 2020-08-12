import sys
import os
sys.path.append('/DEV_TESTS/PythonRunner/examples')
from runner.unittest.setup import Test
from runner.unittest.suite import UnittestSuite
import unittest
from template_class1 import TestConfigInterface
from testcase import TestAssertion2

def suite():
    suites = unittest.TestSuite()
    suites.addTest(TestAssertion2('test_6'))
    suites.addTest(TestAssertion2('test_5'))
    suites.addTest(Test.parametrize(TestConfigInterface, **{'if':'X3', 'dd':4}))
    return suites


if __name__ == '__main__':
   #  to_users = 'wgu@sonicwall.com'
    st = UnittestSuite(sys.argv, suite())
    st.run()
