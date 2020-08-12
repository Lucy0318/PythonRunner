import unittest
from winrunner.settings import Params, LOGGING, DEBUG_LOGGING, debug_logger
from winrunner.testrunner import Runner
logger = LOGGING.getLogger(__name__)

class UnittestSuite(Runner):
    def __init__(self, args, suite, to_users = None, cc_users = None):
        debug_logger.info("--- unittest init start ---")
        logger.info("--- unittest init start ---")
        super().__init__(args, suite, to_users, cc_users)
        debug_logger.debug("--- unittest init end ---")
        logger.info("--- unittest init end ---")

    def run_and_parse_result(self):
        debug_logger.info("--- unittest run and parse start ---")
        runner = unittest.TextTestRunner(verbosity=2)
        debug_logger.info("--- unittest after verbose ---")
        debug_logger.debug("runner output : %s", runner)
        results = runner.run(self.suite)
        debug_logger.debug("runner output :" + str(results))
        debug_logger.info("--- run self.suite --- :" + str(self.suite))
        debug_logger.info("--- after runner.run ---")

        # parse test result
        resultsString = str(results)
        debug_logger.debug("result string :" + str(resultsString))
        resultArray = resultsString.split(" ")
        debug_logger.debug("result array :" + str(resultArray))
        Params.total_run = resultArray[1].split("=")[1]
        debug_logger.debug("result params.total_run :" + str(Params.total_run))
        debug_logger.debug("*** RESULT ARRAY *** :" + str(resultArray))
        debug_logger.debug("*** Total run **** :" + str(Params.total_run))
        Params.total_errors = resultArray[2].split("=")[1]
        debug_logger.debug("*** Params.Total errors *** :" + str(Params.total_errors))
        Params.total_failures = resultArray[3].split('>')[0].split("=")[1]
        debug_logger.debug("*** Params.Total failure *** :" + str(Params.total_failures))
        # Errors make total pass as negative
        # Params.total_pass = int(Params.total_run) - int(Params.total_failures) - int(Params.total_errors)
        Params.total_pass = int(Params.total_run) - int(Params.total_failures)
        debug_logger.debug("*** Params.Total pass *** :" + str(Params.total_pass))
        logger.info("<Run:" + Params.total_run + ", Errors: " + Params.total_errors + ", Failures: " + Params.total_failures + ">")
        debug_logger.info(
            "<Run:" + Params.total_run + ", Errors: " + Params.total_errors + ", Failures: " + Params.total_failures + ">")

        # The values of Params.total_pass, fail, error, skip need to be cleared and set to zero
        # As the same values are used in test runner -> get_result_summary and upgraded as well
        # Total_run is not cleared as it is not used in test runner file in that function.
        Params.total_pass = 0
        Params.total_failures = 0
        Params.total_skip = 0
        Params.total_errors = 0
        debug_logger.debug("The values of Params.total_pass, fail, error, skip need to be cleared and set to zero")
        debug_logger.debug("As the same values are used in test runner -> get_result_summary and upgraded as well")
        debug_logger.debug("Total_run is not cleared as it is not used in test runner file in that function.")
        debug_logger.debug("Params.total_pass" + str(Params.total_pass))
        debug_logger.debug("Params.total_failures" + str(Params.total_failures))
        debug_logger.debug("Params.total_skip" + str(Params.total_skip))
        debug_logger.debug("Params.total_errors" + str(Params.total_errors))

        debug_logger.info("--- unittest run and parse end ---")
