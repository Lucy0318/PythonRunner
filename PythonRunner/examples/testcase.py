from runner.utils.email_util import SendMail
from runner.unittest.setup import Test
from runner.utils.assertion import Assertion
import logging
import unittest
from runner.settings import Params

class TestAssertion1(Test):
    uuid = "1111111111111111111111"
    @classmethod
    def setUpClass(cls):
        logging.info("this method only called once, can use to print testcase description")
    @classmethod
    def tearDownClass(cls):
        print("this method only called once too")  

###if setUp and tearDown not defined here, then call thme in class Test 
    def setUp(self):
        logging.info('----this method called before each method named test_  -----')
    def tearDown(self):
        logging.info('-----this method called after each method named test_  -----')

    def test_1(self):
        print('-----test1----')
        to_users = "test1@sonicwall.com"
        eu = SendMail(to_users)
        Assertion.assert_equal(eu.to_users, 'test1@sonicwall.com', "ERR: ToUsers is not correct")

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

@unittest.skipIf(Params.smk, 'Skip as this is a smk test')
class TestAssertion2(Test):
    uuid = "8A39711E-0464-11DE-860E-445A00F93527"
    def setUp(self):
        super().setUp()
        logging.info('-----teststage setup')
    def tearDown(self):
        super().tearDown()
        logging.info('-----teststage teardown')

    def test_6(self):
        print('-----test6----')
        value1 = 'foo'
        value2 = 'FOO'
        Assertion.assert_not_equal(value1, value2, "ERR: values equal")

    def test_5(self):
        print('-----test5----')
        value1 = 'foo'
        value2 = 'foo'
        Assertion.assert_not_equal(value1, value2, "ERR: values equal")
