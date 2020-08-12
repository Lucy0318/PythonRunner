from runner.utils.email_util import SendMail
from runner.unittest.setup import Test, repeat_method
from runner.utils.assertion import Assertion
import logging
import unittest
from runner.settings import Params

class TestAssertion1(Test):
    uuid = "1111111111111111111111"

    @repeat_method(2)
    def test_1(self):
        print('-----test1----')
        to_users = "test1@sonicwall.com"
        eu = SendMail(to_users)
        Assertion.assert_equal(eu.to_users, 'test2@sonicwall.com', "ERR: ToUsers is not correct")

    def test_3(self):
        print('-----test3----')
        value1 = 'foo'
        value2 = 'FOO'
        Assertion.assert_not_equal(value1, value2, "ERR: values equal")

    def test_2(self):
        print('-----test2----')
        value1 = 'foo'
        value2 = 'foo'
        Assertion.assert_not_equal(value1, value2, "ERR: values equal")

