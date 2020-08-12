from runner.utils.email_util import SendMail
from runner.unittest.setup import Test, skip_if_dts
from runner.utils.assertion import Assertion
import unittest
from runner.settings import Params,logger


class TestAssertion1(Test):
    uuid = "1111111111111111111111"

    def runTest(self):
        types_list_igmp = ["None", "Msg 17 : Member Query", "Msg 18 : V1 Member Report", "Msg 22 : V2 Member Report", 
                           "Msg 23 : Leave Group", "Msg 34 : V3 Member Report"]
        Test.subTestUUID = ['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6']
        Test.subTestName = types_list_igmp
        for n in types_list_igmp:
            with self.subTest(name=n):
                try:
                    logger.info('-----test_traffic----' + str(n))
                    value1 = 'foo'
                    value2 = 'FOO'
                    Assertion.assert_equal(value1.upper(), value2, "ERR: values equal")
                except Exception as err:
                    print(err)

