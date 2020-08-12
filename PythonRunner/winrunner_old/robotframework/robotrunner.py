import sys
from winrunner.settings import Params, LOGGING, LOG_DIR, ROBOT_OUT_FILE, ROBOT_REP_FILE, ROBOT_LOG_FILE, \
    ROBOT_OUT_FILE_WITH_PTAH, ROBOT_REP_FILE_WITH_PATH, ROBOT_LOG_FILE_WITH_PATH
from winrunner.testrunner import Runner
from winrunner.utils.log import log
from robot.api import ExecutionResult, ResultVisitor
import subprocess

logger = LOGGING.getLogger(__name__)


class RobotRunnerException(Exception):
    def __init__(self, info):
        super().__init__(f"RobotRunner error: {info}")

class RobotRunner(Runner):
    def __init__(self, args, suite=None, to_users=None, cc_users=None):
        for i in range(len(args)):
            if args[i] == "--robot" and i<len(args)-1 and args[i+1].endswith("robot"):
                Params.robot = args[i+1]
                break

        if Params.robot == '':
            raise RobotRunnerException("Robot param is missing")
        else:
            super().__init__(args, suite, to_users, cc_users)

    def run_and_parse_result(self):
        print("...run and parse result ....")
        # compose robot command and run it
        robot_cmd = "robot --outputdir " + LOG_DIR + " --log " + ROBOT_LOG_FILE + " --report " + ROBOT_REP_FILE
        robot_cmd += " --output " + ROBOT_OUT_FILE + " " + Params.robot
        try:
            subprocess.call(robot_cmd, shell=True)
        except OSError as e:
            logger.error("Robot command execution failed: ", str(e))
            raise RobotRunnerException("Robot command execution failed")

    def parse_result_file(self):
        output = ExecutionResult(ROBOT_OUT_FILE_WITH_PTAH)
        result_summary = ResultSummary()
        output.visit(result_summary)
        self.results = result_summary.results
        Params.total_run = result_summary.total_run
        Params.total_pass = result_summary.total_pass
        Params.total_errors = result_summary.total_errors
        Params.total_failures = result_summary.total_failures

    def _initiate_log(self):
        pass

    def get_logs_info(self):
        data = []
        my_log = log(Params.resource, Params.product, Params.scmlabel, Params.testbed, Params.user)

        log_url = my_log.copy_file_to_log_server(ROBOT_LOG_FILE_WITH_PATH)

        data.append({
            'Name': 'Log File',
            'Link': log_url,
            'Display': ROBOT_LOG_FILE_WITH_PATH
        })

        rep_url = my_log.copy_file_to_log_server(ROBOT_REP_FILE_WITH_PATH)

        data.append({
            'Name': 'Report File',
            'Link': rep_url,
            'Display': ROBOT_REP_FILE_WITH_PATH
        })

        out_url = my_log.copy_file_to_log_server(ROBOT_OUT_FILE_WITH_PTAH)

        data.append({
            'Name': 'Output File',
            'Link': out_url,
            'Display': ROBOT_OUT_FILE_WITH_PTAH
        })

        console_url = my_log.get_dut_console_log_link()

        data.append({
            'Name': 'DUT Console Logs',
            'Link': console_url,
            'Display': 'console'
        })

        return data


class ResultSummary(ResultVisitor):
    def __init__(self):
        self.results = []
        self.total_run = 0
        self.total_pass = 0
        self.total_errors = 0
        self.total_failures = 0
        self.has_uuid = False

    def visit_test(self, test):
        items = test.doc.split(";")
        uuid = ""
        tc_type = ""
        for item in items:
            temp = item.strip()
            if temp.startswith("UUID:"):
                uuid = temp.replace("UUID:", "")
            elif temp.startswith("Type:"):
                tc_type = temp.replace("Type:", "")

        self.results.append({
            'title': test.name,
            'result': test.status,
            'starttime': test.starttime,
            'endtime': test.endtime,
            'uuid': uuid,
            'matrixid': 0,
            'type': tc_type,
            'parameters': '',
            'alias': '',
            'filename': test.parent.source,
            'log_link': ROBOT_LOG_FILE_WITH_PATH
        })

        self.total_run += 1
        if test.status == "PASS":
            self.total_pass += 1
        elif test.status == "FAIL":
            self.total_failures += 1
        else:
            self.total_errors += 1

        if not self.has_uuid and uuid != "":
            self.has_uuid = True


if __name__ == '__main__':
    st = RobotRunner(sys.argv)
    st.run()
