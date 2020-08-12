import sys
import os
sys.path.append('/DEV_TESTS/PythonRunner/examples')
from runner.unittest.setup import Test
from runner.unittest.suite import UnittestSuite
import unittest
from template_class import TestConfigInterface

def suite():
    testcases_list=['template_class']
    suites=unittest.TestLoader().loadTestsFromNames(testcases_list)
    return suites


if __name__ == '__main__':
    # to_users = 'wgu@sonicwall.com'
    st = UnittestSuite(sys.argv, suite())
    st.run()
