from testcase import TestAssertion1
from testcase import TestAssertion2
from runner.unittest.suite import UnittestSuite
import unittest
import sys

#this suite will run all testcase in *test*.py under case_path
def suite():
    case_path = '/SWIFT4.0/PythonRunner/examples'
    suites=unittest.defaultTestLoader.discover(case_path,pattern="*test*.py",top_level_dir=None)
    return suites


if __name__ == '__main__':
    # to_users = 'wgu@sonicwall.com'
    # cc_users = 'automation, shanghai_automation'
    st = UnittestSuite(sys.argv, suite())
    st.run()
