from runner.utils.email_util import SendMail
from runner.unittest.setup import Test, skip_if_fail_method
from runner.utils.assertion import Assertion
import logging

class TestAssertion1(Test):
    uuid = "1111111111111111111111"
    @classmethod
    def setUpClass(cls):
        logging.info("this method only called once, can use to print testcase description")
    @classmethod
    def tearDownClass(cls):
        print("this method only called once too")  

    def test_login(self):
        print('-----test_login----')
        Assertion.assert_equal(1, 2, "ERR: value not equal")

    @skip_if_fail_method(depend='test_login')
    def test_traffic(self):
        print('-----test_traffic----')
        value1 = 'foo'
        value2 = 'FOO'
        Assertion.assert_not_equal(value1, value2, "ERR: values equal")

    def test_logout(self):
        print('-----test_traffic----')
        value1 = 'foo'
        value2 = 'FOO'
        Assertion.assert_not_equal(value1.upper(), value2, "ERR: values equal")

if __name__ == '__main__':
    import unittest
    unittest.main()