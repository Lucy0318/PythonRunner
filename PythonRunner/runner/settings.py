import logging
import re
import os
import sys
import datetime
import time
from pathlib import Path
from urllib import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jinja2 import Environment, FileSystemLoader
# log file and result file

def dirsort(alist):
    try:
        alist.sort(key= lambda x: int(re.findall('\d+$', x)[0]))
    except:
        pass
    return alist

def setup_logdir(LOG_DIR):
    dir_prefix = os.environ['USER'] + '_pythonrunner_'
    new_dirs = []
    for root, dirs, files in os.walk(LOG_DIR):
        if root == LOG_DIR:
            new_dirs = dirs[::]
            for each in dirs:
                if not re.search(r'^' + dir_prefix + '\d*$', each):
                    new_dirs.remove(each)
            dirsort(new_dirs)
            break
    if not new_dirs:
        index = 0
    else:
        index = int(re.search(r'' + dir_prefix + '(\d*)', new_dirs[-1]).group(1)) + 1
    LOG_DIR += '/' + dir_prefix + str(index)
    return LOG_DIR

SUITE_FILE = os.path.basename(sys.argv[0]).split(".")
TIMESTAMP = str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_")
TIMENOW = time.strftime("%s", time.gmtime())
SUITE_LOG_FILE = "commands.log"
FAILED_SUITE_LOG_FILE = 'Failed_testcase' + ".log"
SUITE_RES_FILE = 'summary' + ".csv"
SUITE_COMMAND_LINE_FILE = "command_line.log"
SUITE_PYTHON_FILE = "python_runner.log"
LOG_DIR = os.path.join(os.path.expanduser("~"), "Python_Runner_Logs")
LOG_DIR = setup_logdir(LOG_DIR)
os.path.exists(LOG_DIR) or os.makedirs(LOG_DIR)
SUITE_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_LOG_FILE)
FAILED_SUITE_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR,FAILED_SUITE_LOG_FILE)
SUITE_RES_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_RES_FILE)
SUITE_COMMAND_LINE_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_COMMAND_LINE_FILE)
SUITE_PYTHON_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_PYTHON_FILE)
# robotframework log files
ROBOT_LOG_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_log.html"
ROBOT_REP_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_report.html"
ROBOT_OUT_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_output.xml"
ROBOT_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR, ROBOT_LOG_FILE)
ROBOT_REP_FILE_WITH_PATH = os.path.join(LOG_DIR, ROBOT_REP_FILE)
ROBOT_OUT_FILE_WITH_PTAH = os.path.join(LOG_DIR, ROBOT_OUT_FILE)

# logging
DEBUG2 = 9
LOGGING = logging
LOGGING.addLevelName(DEBUG2, "DEBUG2")
LOGGING.basicConfig(
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(SUITE_LOG_FILE_WITH_PATH),
        logging.StreamHandler()
    ]
)
logger = LOGGING.getLogger(__name__)
python_logger = open(SUITE_PYTHON_FILE_WITH_PATH, 'a', newline='')

def debug2(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG2):
        self._log(DEBUG2, message, args, **kws)
LOGGING.Logger.debug2 = debug2

# SonicAuto
SONICAUTO_CONN = "postgres://sonicauto:%s@10.203.15.9:5432/sonicauto" % parse.unquote('s0nicw@ll')
SONICAUTO_SESSION = sessionmaker(create_engine(SONICAUTO_CONN))

def get_sonicauto_session():
    return SONICAUTO_SESSION()

# mail server
MAIL_SVR = '10.50.129.54'
DEFAULT_FROM_USER = 'auto_email@sonicwall.com'
DEFAULT_CC_USER = 'automation@sonicwall.com, shanghai_automation@sonicwall.com'

# job related variables
try:
    QBS_JOBNUM = os.environ['QBS_JOBNUM']
except:
    QBS_JOBNUM = '111111'

# parameters
class Params:
    cc = ''
    scmlabel = '1.1.1.1'
    testbed = ''
    avt_mountpoint = ''
    build = ''
    prebuild = ''
    tenant_build = ''
    product = ''
    user = ''
    requesttime = ''
    mount_point = ''
    qbs = '1'
    resource = ''
    bundle = False
    rgname = ''
    openstack = ''
    setuptestbed = ''
    setupjoblog = ''
    openstack_tid = ''
    starttime = ''
    log_level = ''
    log_dir = ''
    version = ''
    sonicos_ver = ''
    trialrun = False
    no_database = False
    command = ''
    log_location = SUITE_LOG_FILE_WITH_PATH
    path = ''
    db_upload = 'Yes'
    qbsjobid = QBS_JOBNUM
    ts_actual_name = ''
    total_aptest = 0
    finishtime = ''
    total_run = 0
    total_errors = 0
    total_skip = 0
    total_failures = 0
    total_pass = 0
    nontc_total_run = 0
    nontc_total_errors = 0
    nontc_total_skip = 0
    nontc_total_failures = 0
    nontc_total_pass = 0
    reg_total_exec = 0
    reg_exec_time = 0
    ts_display_name = ''
    exec_time = ''
    total_exec= 0
    robot = ''
    dts_jira_link = {}
    ##for UI7
    browser_type = 'firefox'
    test_type = 'ui'
    
###description for testcase and test stage which show in mail
class Descriptions:
    testcase = []
    teststage = []

class TestcaseLog:
    log = {}

# PythonRunner Home Dir
try:
    PYTHON_RUNNER_HOME = os.environ['PYTHON_RUNNER_HOME']
except:
    PYTHON_RUNNER_HOME = '/SWIFT4.0/PythonRunner'

# Email templates
TEMPLATE_DIR = os.path.join(PYTHON_RUNNER_HOME, "runner/resources/templates/email")
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
TEST_COMPLETED_TEMPLATE = TEMPLATE_ENV.get_template("test_completed.html")
START_TEST_COMPLETED_TEMPLATE = TEMPLATE_ENV.get_template("start_test_completed.html")