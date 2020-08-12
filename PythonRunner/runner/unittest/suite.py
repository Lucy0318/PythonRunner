import unittest
from runner.settings import Params, logger
from runner.testrunner import Runner

class UnittestSuite(Runner):
    def __init__(self, args, suite, to_users = None, cc_users = None, resultclass=None):
        super().__init__(args, suite, to_users, cc_users)
        self.resultclass = resultclass

    def run_and_parse_result(self):
        runner = unittest.TextTestRunner(verbosity=2, resultclass=self.resultclass)
        results = runner.run(self.suite)

        # parse test result
        resultsString = str(results)
        resultArray = resultsString.split(" ")
        # Params.total_run = resultArray[1].split("=")[1]
        # Params.total_errors = resultArray[2].split("=")[1]
        # Params.total_failures = resultArray[3].split('>')[0].split("=")[1]
        # Params.total_pass = int(Params.total_run) - int(Params.total_failures) - int(Params.total_errors)
        #logger.info("<Run Testcase:" + str(Params.total_run) + ", Skipped: " + str(Params.total_skip) + ", Failures: " + str(Params.total_failures) + ">")
        #logger.info("<Run NonTC:" + str(Params.nontc_total_run) + ", Skipped: " + str(Params.nontc_total_skip) + ", Failures: " + str(Params.nontc_total_failures) + ">")
