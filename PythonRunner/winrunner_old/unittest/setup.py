import unittest
import datetime
import csv
import os
from winrunner.settings import LOGGING, SUITE_RES_FILE_WITH_PATH, Descriptions, TestcaseLog, LOG_DIR, Params, logger, debug_logger


def skip_if_fail_method(depend=None):
    import functools
    def wraper_func(test_func):
        @functools.wraps(test_func)
        def inner_func(self):
            if depend == test_func.__name__:
                raise ValueError("{} cannot depend on itself".format(depend))
            failures = str([fail[0] for fail in self._outcome.result.failures])
            errors = str([error[0] for error in self._outcome.result.errors])
            skipped = str([skip[0] for skip in self._outcome.result.skipped])
            flag = (depend in failures) or (depend in errors) or (depend in skipped)
            test = unittest.skipIf(flag, '{} failed  or  error or skipped'.format(depend))(test_func)
            debug_logger.debug("failures : %s", str(failures))
            debug_logger.debug("errors : %s", str(errors))
            debug_logger.debug("skipped : %s", str(skipped))
            debug_logger.debug("test : %s", str(test))
            debug_logger.debug("test(self) : %s", str(test(self)))
            return test(self)
        return inner_func
    return wraper_func


class NumbersTestResult(unittest.TextTestResult):
    def addSubTest(self, test, subtest, outcome):
        super(NumbersTestResult, self).addSubTest(test, subtest, outcome)
        # add to total number of tests run
        test.subTestTearDown(outcome, test.subTestName[self.testsRun - 1], test.subTestUUID[self.testsRun - 1])
        self.testsRun += 1


class Test2(unittest.TestCase):
    def __init__(self, methodName='runTest', param=None, **kwargs):
        super().__init__(methodName)
        self.test_case_name = unittest.TestCase.id(self)
        self.test_case_name_string = str(self.test_case_name)
        self.splitted_name = self.test_case_name_string.split(".")
        self.splitted_name_len = self.splitted_name.__len__()
        self.test_case_id = self.splitted_name[self.splitted_name_len-2]
        self.test_method_id = self.splitted_name[self.splitted_name_len-1]
        self.kwargs = kwargs
        debug_logger.debug("test_case_name_string : %s", str(self.test_case_name_string))
        debug_logger.debug("splitted_name : %s", str(self.splitted_name))
        debug_logger.debug("test_case_id : %s", str(self.test_case_id))
        debug_logger.debug("test_method_id : %s", str(self.test_method_id))
        debug_logger.debug("kwargs : %s", str(self.kwargs))


    @staticmethod    
    def parametrize(testcase_klass, **kwargs):    
        """ Create a suite containing all tests taken from the given  
            subclass, passing them the parameter 'kwargs'.  
        """    
        testloader = unittest.TestLoader()
        debug_logger.debug("testloader : %s", str(testloader))
        testnames = testloader.getTestCaseNames(testcase_klass)
        debug_logger.debug("testnames : %s", str(testnames))
        suite = unittest.TestSuite()
        debug_logger.debug("suite : %s", str(suite))
        for name in testnames:    
            suite.addTest(testcase_klass(name, **kwargs))
            debug_logger.debug("suite : %s", str(suite))
        return suite    
    
    @classmethod
    def setUpClass(cls):
        print("CLS : ", cls)
        cls.start_time = str(datetime.datetime.now().replace(microsecond=0))
        cls.test_case_id = cls.__name__
        print("LOG_DIR :", LOG_DIR)
        debug_logger.debug("------------------------- TEST CASE : " + str(cls.test_case_id) + "-----------------------")
        debug_logger.debug("-----------------------------------------------------------------------------------------"
                           "------------------------------------")
        debug_logger.debug("LOG DIR : %s", str(LOG_DIR))
        case_log_dir = LOG_DIR + '/' + cls.test_case_id
        print("case_log_dir : ", case_log_dir)
        debug_logger.debug("case_log_dir : %s", str(case_log_dir))
        case_log = case_log_dir + '/' + cls.test_case_id + '.log'
        print("case_log : ", case_log)
        debug_logger.debug("case_log : %s", str(case_log))
        os.path.exists(case_log_dir) or os.makedirs(case_log_dir)
        Test2.test_case_result = 'PASSED'
        debug_logger.debug("Test2.test_case_result : %s", str(Test2.test_case_result))
        Descriptions.teststage.append({cls.test_case_id: {}})  
        TestcaseLog.log[cls.test_case_id] = case_log
        cls.handler = LOGGING.FileHandler(case_log, mode='w')
        formatter1 = LOGGING.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
        cls.handler.setFormatter(formatter1)
        cls.handler.setLevel(Params.log_level)
        logger.addHandler(cls.handler)
        logger.info("########## STARTING CASE: " + cls.test_case_id + " ##########")
        debug_logger.debug("########## STARTING CASE: %s ##########", str(cls.test_case_id))


    @classmethod
    def tearDownClass(cls):
        cls.uuid = Test2.uuid
        debug_logger.debug("Test2.uuid : %s", str(cls.uuid))
        if not cls.uuid or cls.uuid != 'NonTC':
            try:
                Descriptions.testcase.append({Test2.test_case_id: Test2.description})
            except Exception as e:
                logger.warning('description not defined when this is a testcase.')
                debug_logger.warning("description not defined when this is a testcase.")
        # append the result to csv file
        cls.end_time = str(datetime.datetime.now().replace(microsecond=0))
        debug_logger.debug("cls.end_time : %s", str(cls.end_time))
        output_file = open(SUITE_RES_FILE_WITH_PATH, 'a', newline='')
        debug_logger.debug("output_file : %s", str(output_file))
        logger.debug("SUITE_RES_FILE_WITH_PATH : " + SUITE_RES_FILE_WITH_PATH)
        debug_logger.debug("SUITE_RES_FILE_WITH_PATH : " + SUITE_RES_FILE_WITH_PATH)
        a = csv.writer(output_file, delimiter=',')
        # logger.debug("csv.writer" + a)
        # debug_logger.debug("csv.writer" + str(a))
        a.writerow([Test2.test_case_id, Test2.test_case_result, cls.start_time, cls.end_time, cls.uuid])
        output_file.close()
        logger.info("########## Testcase: " + Test2.test_case_id + ' '*3 + Test2.test_case_result + "  ##########" + '\n'*2)
        debug_logger.info(
            "########## Testcase: " + str(Test2.test_case_id) + ' ' * 3 + str(Test2.test_case_result) + "  ##########" + '\n' * 2)
        logger.removeHandler(cls.handler)

    def setUp(self):
        logger.info("########## STARTING METHOD: " + self.test_method_id + " ##########")
        debug_logger.info("########## STARTING METHOD: " + self.test_method_id + " ##########")
        Test2.test_case_id = self.test_case_id
        debug_logger.debug("Test2.test_case_id :" + Test2.test_case_id)

    def tearDown(self):
        Test2.uuid = self.uuid
        debug_logger.debug("Test2.uuid :" + Test2.uuid)
        Test2.description = self.description
        debug_logger.debug("Test2.description :" + Test2.description)
        # fetch the test result according to
        # http://stackoverflow.com/questions/4414234/getting-pythons-unittest-results-in-a-teardown-method
        if hasattr(self, '_outcome'):
            result = self.defaultTestResult()
            debug_logger.debug("result :" + str(result))
            self._feedErrorsToResult(result, self._outcome.errors)
        else:
            result = getattr(self, '_outcomeForDoCleanups', self._resultForDoCleanups)
            debug_logger.debug("Result :" + result)
        error = self.list2reason(result.errors)
        debug_logger.debug("Error :" + str(error))
        failure = self.list2reason(result.failures)
        debug_logger.debug("Failure :" + str(failure))
        ok = not error and not failure
        debug_logger.debug("ok :" + str(ok))

        test_result = None
        if not ok:
            typ, text = ('ERROR', error) if error else ('FAIL', failure)

            if str(typ)== "FAIL" or str(typ)== "ERROR":
                logger.info(self.test_method_id + ": Failed")
                debug_logger.info(self.test_method_id + ": Failed")
                test_result = "FAILED"
        else:
            logger.info(self.test_method_id + ": Passed")
            debug_logger.info(self.test_method_id + ": Passed")
            test_result = "PASSED"
    
        if test_result == 'FAILED':
            Test2.test_case_result = 'FAILED'
            debug_logger.debug("Test2.test_case_result :" + Test2.test_case_result)
            try:
                Descriptions.teststage[-1][self.test_case_id][self.test_method_id] = 'failed'
            except Exception as e:
                logger.warning('Descriptions.teststage failed')
                debug_logger.debug("Descriptions.teststage failed :" + Descriptions.teststage)
        Test2.test_case_id = self.test_case_id
        debug_logger.debug("Test2.test_case_id" + Test2.test_case_id)

    def subTest(self, *args, **kwargs):
        try:
            super().subTest(msg=None, **kwargs)
        except AttributeError:
            super().subTest = contextlib.contextmanager(lambda *a, **kw: (yield))
        return super().subTest(*args, **kwargs)

    def subTestTearDown(self, outcome, test_case_id, uuid):
        if outcome is not None:
            logger.error(test_case_id + ": FAILED")
            debug_logger.error(test_case_id + ": FAILED")
            self.test_case_result = "FAILED"
        else:
            logger.info(test_case_id + ": PASSED")
            debug_logger.info(test_case_id + ": PASSED")
            self.test_case_result = "PASSED"
        self.end_time = str(datetime.now().replace(microsecond=0))
        debug_logger.debug("Endtime :" + self.end_time)
        output_file = open(result_csv, 'a', newline='')
        debug_logger.debug("Output File :" + output_file)
        a = csv.writer(output_file, delimiter=',')
        debug_logger.debug("a : csv writer " + a)
        a.writerow([test_case_id, self.test_case_result, self.start_time, self.end_time, uuid])
        output_file.close()
        logger.info("########## SubTest Case: " + test_case_id + ' ' * 3 + self.test_case_result + "  ##########" + '\n' * 2)
        debug_logger.debug(
            "########## SubTest Case: " + test_case_id + ' ' * 3 + self.test_case_result + "  ##########" + '\n' * 2)

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            debug_logger.debug("exc_list :" + str(exc_list))
            debug_logger.debug("return exc_list[-1][1] :" + str(exc_list[-1][1]))
            return exc_list[-1][1]
