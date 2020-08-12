import unittest
import traceback
from winrunner.settings import LOGGING

logger = LOGGING.getLogger(__name__)


class Assertion(unittest.TestCase):
    @classmethod
    def assert_equal(cls, actual_output, expected_output, msg):
        logger.info("actual output is:")
        logger.info(actual_output)
        logger.info("expected output is:")
        logger.info(expected_output)
        try:
            assert actual_output == expected_output, msg
        except AssertionError as e:
            logger.error(traceback.format_exc(), "error")
            raise e

    @classmethod
    def assert_not_equal(cls, actual_output, expected_output, msg):
        logger.info("actual output is:")
        logger.info(actual_output)
        logger.info("expected output is:")
        logger.info(expected_output)
        try:
            assert actual_output != expected_output, msg
        except AssertionError as e:
            logger.error(traceback.format_exc(), "error")
            raise e

    @classmethod
    def assert_raises(cls, methodToRun, expected_exception, msg):
        try:
            with Assertion.assertRaises(cls, expected_exception=expected_exception) as cm:
                methodToRun()
        except Exception as e:
            logger.error("actual exception is:")
            logger.error(e)
            logger.error("expected exception is:")
            logger.error(expected_exception)
            logger.error(msg)
            logger.error(traceback.format_exc(), "error")
            raise e

        logger.info("actual exception is:")
        logger.info(cm.exception)
        logger.info("expected exception is:")
        logger.info(expected_exception)
