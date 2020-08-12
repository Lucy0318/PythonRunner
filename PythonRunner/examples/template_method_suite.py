import sys
import os
sys.path.append('/DEV_TESTS/PythonRunner/examples')

from runner.unittest.suite import UnittestSuite
import unittest


def suite():
    testcases_list=['template_method.TestConfigInterface']
    suites=unittest.TestLoader().loadTestsFromNames(testcases_list)
    return suites


if __name__ == '__main__':
    # to_users = 'wgu@sonicwall.com'
    st = UnittestSuite(sys.argv, suite())
    st.run()
