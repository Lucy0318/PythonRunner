from runner.utils.email_util import SendMail
from runner.unittest.setup import Test, skip_if_dts
from runner.utils.assertion import Assertion
import unittest
from runner.settings import Params
dts_dict= {
    'TestEmailUtilInit': '3354',
}

@skip_if_dts(dts_dict)
class TestEmailUtilInit(Test):
    #uuid = "8A39711E-0464-11DE-860E-445A00F93527"
    uuid = "NonTC"
    dts = '3545'

    @classmethod
    def setUpClass(cls):
        print("this method only called once, can use to print testcase description")
    @classmethod
    def tearDownClass(cls):
        print("this method only called once too")  


    def runTest(self):
        to_users = "wgu@sonicwall.com"
        eu = SendMail(to_users, 'wgu@sonicwall.com')
        Assertion.assert_equal(eu.to_users, 'cliu@sonicwall.com', "ERR: ToUsers is not correct")

class TestAssertion1(Test):
    uuid = "1111111111111111111111"
    @classmethod
    def setUpClass(cls):
        print("this method only called once, can use to print testcase description")
    @classmethod
    def tearDownClass(cls):
        print("this method only called once too")  

    def runTest(self):
        print('-----test_traffic----')
        value1 = 'foo'
        value2 = 'FOO'
        Assertion.assert_not_equal(value1.upper(), value2, "ERR: values equal")

if __name__ == '__main__':
    import unittest
    unittest.main()
