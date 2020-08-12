import unittest
import datetime
import time
import csv
import os
import re
import contextlib
import subprocess

from runner.settings import LOGGING, SUITE_RES_FILE_WITH_PATH, Descriptions, TestcaseLog, LOG_DIR, Params, logger, python_logger
FAILED_TESTCASE = []

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
            test = unittest.skipIf(flag, '{} SKIPPED as {} failed or error or skipped'.format(test_func.__name__, depend))(test_func)
            return test(self)
        return inner_func
    return wraper_func

# def skip_if_fail_class(depend=None):
#     import functools
#     print('----------------------')
#     def wraper_class(test_cls):
#         # @functools.wraps(test_cls)
#         def inner_class( methodName='runTest'):
#             print(TestAssertion1.test_case_result)
#             print(test_cls.__name__)
#             if depend == test_cls.__name__:
#                 raise ValueError("{} cannot depend on itself".format(depend))
#             # failures = str([fail[0] for fail in cls._outcome.result.failures])
#             # errors = str([error[0] for error in cls._outcome.result.errors])
#             # skipped = str([skip[0] for skip in cls._outcome.result.skipped])
#             # flag = (depend in failures) or (depend in errors) or (depend in skipped)
#             test = unittest.skipIf(True, '{} SKIPPED as {} failed or error or skipped'.format(test_cls.__name__, depend))(test_cls)
#             return test(test_cls)
#         return inner_class
#     return wraper_class


def skip_if_dts(dts):
    import functools
    def wraper_func(newcls):
        @functools.wraps(newcls)
        def inner_func():
            if newcls.__name__ in dts:
                flag = True
                newcls.start_time = str(datetime.datetime.now().replace(microsecond=0))
                output_file = open(SUITE_RES_FILE_WITH_PATH, 'a', newline='')
                a = csv.writer(output_file, delimiter=',')
                a.writerow([newcls.__name__, 'SKIPPED', newcls.start_time, newcls.start_time, '----'])
                output_file.close()
                logger.info("########## Testcase: " + newcls.__name__ + ' '*3 + 'SKIPPED' + "  ##########" + '\n'*2)
            else:
                flag = False
            test = unittest.skipIf(flag, "########## Testcase: {} SKIPPED due to dts ##########\n\n".format(newcls.__name__))(newcls)
            return test()
        return inner_func
    return wraper_func

def skip_if_fail_class(depend=None):
    import functools
    def wraper_func(test_func):
        @functools.wraps(test_func)
        def inner_func(self):
            if depend in FAILED_TESTCASE:
                flag = True
            else:
                flag = False
            test = unittest.skipIf(flag, "########## Teststage: {} SKIPPED due to {} failed ##########\n\n".format(test_func.__name__, depend))(test_func)
            return test()
        return inner_func
    return wraper_func

def repeat_method(repeat):
    import functools
    def wraper_func(testfunc):
        @functools.wraps(testfunc)
        def wrapper(self):
            for i in range(repeat):
                logger.info(f'Run for {i} time')
                try:
                    re = testfunc(self)
                    logger.info('-------------------')
                    logger.info(re)
                    return re
                except Exception as e:
                    self.failure = True
                    Test.tearDown(self)
                    Test.setUp(self)
            raise Exception
        return wrapper
    return wraper_func

def repeat_class(repeat):
    import functools
    def wraper_cls(test_cls):
        @functools.wraps(test_cls)
        def inner_cls():
            for i in range(repeat):
                logger.info(f'Run for {i} time')
                try:
                    re = test_cls()

                    logger.info('-------------------')
                    logger.info(Test.test_case_result)
                    return re
                except Exception as e:
                    # self.failure = True
                    print('####################')
                    Test.tearDownClass()
                    Test.setUpClass()
            raise Exception
        return inner_cls
    return wraper_cls

class NumbersTestResult(unittest.TextTestResult):
    def addSubTest(self, test, subtest, outcome):
        super(NumbersTestResult, self).addSubTest(test, subtest, outcome)
        # add to total number of tests run
        test.subTestTearDown(outcome, test.subTestName[test.subTestCount], test.subTestUUID[test.subTestCount])
        self.testsRun += 1
        test.subTestCount += 1

class Test(unittest.TestCase):
    def __init__(self, methodName='runTest', **param):
        super().__init__(methodName)
        self.test_case_name = unittest.TestCase.id(self)
        self.test_case_name_string = str(self.test_case_name)
        self.splitted_name = self.test_case_name_string.split(".")
        self.splitted_name_len = self.splitted_name.__len__()
        self.test_case_id = self.splitted_name[self.splitted_name_len-2]
        self.test_method_id = self.splitted_name[self.splitted_name_len-1]
        self.param = param

    @staticmethod    
    def parametrize(testcase_klass, **kwargs):    
        """ Create a suite containing all tests taken from the given  
            subclass, passing them the parameter 'kwargs'.  
        """    
        testloader = unittest.TestLoader()    
        testnames = testloader.getTestCaseNames(testcase_klass)    
        suite = unittest.TestSuite()    
        for name in testnames:    
            suite.addTest(testcase_klass(name, **kwargs))    
        return suite    
    
    @classmethod
    def setUpClass(cls):
        Test.test_case_result = 'PASSED'
        cls.start_time = str(datetime.datetime.now().replace(microsecond=0))
        cls.test_case_id = cls.__name__
        Params.dts_jira_link[cls.test_case_id] = ''
        Descriptions.description = cls.test_case_id
        python_logger.write('Entering Testcase: ' + cls.test_case_id + ' at ' + time.asctime( time.localtime(time.time())) + '\n')
        case_log_dir = LOG_DIR + '/' + cls.test_case_id
        # case_log = case_log_dir + '/' + cls.test_case_id + '.log'
        relative_case_log = cls.test_case_id + '/' + cls.test_case_id + '.log'
        os.path.exists(case_log_dir) or os.makedirs(case_log_dir)
        Descriptions.teststage.append({cls.test_case_id: {}})  
        TestcaseLog.log[cls.test_case_id] = relative_case_log
        cls.handler = LOGGING.FileHandler(case_log_dir + '/' + cls.test_case_id + '.log', mode='w')
        formatter1 = LOGGING.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s] - %(message)s')
        if Params.log_level == 'DEBUG2':
            formatter1 = LOGGING.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] - %(message)s')
        cls.handler.setFormatter(formatter1)
        cls.handler.setLevel(Params.log_level)
        logger.addHandler(cls.handler)
        logger.info("########## STARTING CASE: " + cls.test_case_id + " ##########")

    @classmethod
    def tearDownClass(cls):
        cls.uuid = Test.uuid
        Descriptions.testcase.append({cls.test_case_id: Descriptions.description})

        # if not cls.uuid or cls.uuid != 'NonTC':
        #     try:
        #         Descriptions.testcase.append({Test.test_case_id: Test.description})
        #     except Exception as e:
        #         logger.warning('description not defined when this is a testcase.')
        # append the result to csv file
        cls.end_time = str(datetime.datetime.now().replace(microsecond=0))
        output_file = open(SUITE_RES_FILE_WITH_PATH, 'a', newline='')
        a = csv.writer(output_file, delimiter=',')
        a.writerow([cls.test_case_id, Test.test_case_result, cls.start_time, cls.end_time, cls.uuid])
        output_file.close()
        logger.info("########## Testcase: " + cls.test_case_id + ' '*3 + Test.test_case_result + "  ##########" + '\n'*2)
        logger.removeHandler(cls.handler)
        python_logger.write('Exting Testcase: ' + cls.test_case_id + ' at ' + time.asctime( time.localtime(time.time())) + ' ... Result: ' + Test.test_case_result + '\n')
        if Test.test_case_result == 'FAILED':
            FAILED_TESTCASE.append(cls.test_case_id)

    def setUp(self):
        self.failure = False
        python_logger.write('Entering stage: ' + self.test_case_id + ' at ' + time.asctime( time.localtime(time.time()))+ '\n')
        logger.info("########## STARTING METHOD: " + self.test_method_id + " ##########")
        Test.test_case_id = self.test_case_id
        #Test.test_case_result = 'PASSED'

    def tearDown(self):
        Test.uuid = self.uuid
        Test.subTestCount = 0
        try:
            Descriptions.description = self.test_case_id + ' - ' + self.description
        except:
            Descriptions.description = self.test_case_id
        try:
            if re.search(r'^\d+$', self.dts):
                Params.dts_jira_link[self.test_case_id] = 'https://sonicdts.eng.sonicwall.com/update_bug.asp?jobid=' + str(self.dts)  
        except:
            try:
                if re.search(r'^\w*-\d*$', self.jira):
                    Params.dts_jira_link[self.test_case_id] = 'https://track.eng.sonicwall.com/browse/' + str(self.jira).upper()
            except:
                pass
                 
        # fetch the test result according to
        # http://stackoverflow.com/questions/4414234/getting-pythons-unittest-results-in-a-teardown-method
        if hasattr(self, '_outcome'):
            result = self.defaultTestResult()
            self._feedErrorsToResult(result, self._outcome.errors)
        else:
            result = getattr(self, '_outcomeForDoCleanups', self._resultForDoCleanups)
        self.error = self.list2reason(result.errors)
        self.failure = self.list2reason(result.failures) if not self.failure else True
        self.skipped = self.list2reason(result.skipped)

        ok = not self.error and not self.failure
        test_result = None
        if not ok:
            typ, text = ('ERROR', self.error) if self.error else ('FAIL', self.failure)

            if str(typ)== "FAIL" or str(typ)== "ERROR":
                logger.info("########## Method: " + self.test_method_id + ' Failed' + "  ##########" + '\n')
                test_result = "FAILED"
        elif self.skipped:
            logger.info("########## Method: " + self.test_method_id + ' Skipped' + "  ##########" + '\n')
        else:
            logger.info("########## Method: " + self.test_method_id + ' Passed' + "  ##########" + '\n')
            test_result = "PASSED"
    
        if test_result == 'FAILED':
            Test.test_case_result = 'FAILED'
            try:
                Descriptions.teststage[-1][self.test_case_id][self.test_method_id] = 'failed'
            except Exception as e:
                logger.warning('Warn: {}'.format(e))
        Test.test_case_id = self.test_case_id
        python_logger.write('Exiting stage: ' + self.test_case_id + ' at ' + time.asctime( time.localtime(time.time()) ) + '... Result: ' + test_result + '\n'*2)


    def subTest(self, *args, **kwargs):
        python_logger.write('Entering Sub-Testcase: ' + kwargs['name'] + ' at ' + time.asctime( time.localtime(time.time()))+'\n')
        try:
            logger.info("########## STARTING SUBTEST CASE: " + kwargs['name'] + " ##########")
            super().subTest(msg=None, **kwargs)
        except AttributeError:
            super().subTest = contextlib.contextmanager(lambda *a, **kw: (yield))
        return super().subTest(*args, **kwargs)

    def subTestTearDown(self, outcome, test_case_id, uuid):
        if outcome is not None:
            logger.error(test_case_id + ": FAILED")
            self.test_case_result = "FAILED"
        else:
            logger.info(test_case_id + ": PASSED")
            self.test_case_result = "PASSED"
        self.end_time = str(datetime.datetime.now().replace(microsecond=0))
        output_file = open(SUITE_RES_FILE_WITH_PATH, 'a', newline='')
        a = csv.writer(output_file, delimiter=',')
        a.writerow([test_case_id, self.test_case_result, self.start_time, self.end_time, uuid])
        output_file.close()
        logger.info("########## SubTest Case: " + test_case_id + ' ' * 3 + self.test_case_result + "  ##########" + '\n' * 3)
        python_logger.write('Exting Sub-Testcase: ' + test_case_id + ' at ' + time.asctime( time.localtime(time.time())) + ' ... Result: ' + self.test_case_result + '\n')

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

