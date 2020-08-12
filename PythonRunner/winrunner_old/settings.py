import logging
import os
import sys
import datetime
from urllib import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jinja2 import Environment, FileSystemLoader
sys.path
# log file and result file
SUITE_FILE = os.path.basename(sys.argv[0]).split(".")
TIMESTAMP = str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "_")
SUITE_LOG_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + ".log"
SUITE_DEBUG_LOG_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_debug" + ".log"
FAILED_SUITE_LOG_FILE = 'Failed_' + SUITE_FILE[0] + "_" + TIMESTAMP + ".log"
SUITE_RES_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + ".csv"
SUITE_COMMAND_LINE_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_command_line.log"
LOG_DIR = os.path.join(os.path.expanduser("~"), "Python_Runner_Logs")
os.path.exists(LOG_DIR) or os.makedirs(LOG_DIR)
SUITE_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_LOG_FILE)
FAILED_SUITE_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR, FAILED_SUITE_LOG_FILE)
SUITE_RES_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_RES_FILE)
SUITE_COMMAND_LINE_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_COMMAND_LINE_FILE)
SUITE_DEBUG_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR, SUITE_DEBUG_LOG_FILE)


# robotframework log files
ROBOT_LOG_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_log.html"
ROBOT_REP_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_report.html"
ROBOT_OUT_FILE = SUITE_FILE[0] + "_" + TIMESTAMP + "_output.xml"
ROBOT_LOG_FILE_WITH_PATH = os.path.join(LOG_DIR, ROBOT_LOG_FILE)
ROBOT_REP_FILE_WITH_PATH = os.path.join(LOG_DIR, ROBOT_REP_FILE)
ROBOT_OUT_FILE_WITH_PATH = os.path.join(LOG_DIR, ROBOT_OUT_FILE)

# loggingtearDownClass
LOGGING = logging
DEBUG_LOGGING = logging

'''LOGGING.basicConfig(
    # format='[%(asctime)s] [%(levelname)s] - %(message)s',
    format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(SUITE_LOG_FILE_WITH_PATH),
        logging.StreamHandler()
    ]
)'''

# Creating two log files, log and debug log
# The link for log file is sent in the mail
# Debug log is stored in the same location but not added to the mail. Only for debug purpose
formatter1 = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s')
handler = logging.FileHandler(SUITE_LOG_FILE_WITH_PATH)
handler.setFormatter(formatter1)
debug_logger = logging.getLogger(__name__)
debug_logger.setLevel(logging.INFO)
debug_logger.addHandler(handler)

formatter2 = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s')
handler = logging.FileHandler(SUITE_DEBUG_LOG_FILE_WITH_PATH)
handler.setFormatter(formatter2)
debug_loggername = __name__ + '2'
debug_logger = logging.getLogger(debug_loggername)
debug_logger.setLevel(logging.DEBUG)
debug_logger.addHandler(handler)

logger = LOGGING.getLogger(__name__)
debug_logger = DEBUG_LOGGING.getLogger(debug_loggername)

# ====================================================================================================
# Print logger and debug logger
debug_logger.debug(" LOGGING : %s", str(logger))
debug_logger.debug(" DEBUG_LOGGING: %s", str(debug_logger))

# Logging all the paths
debug_logger.debug("SUITE_LOG_FILE_WITH_PATH : %s", str(SUITE_LOG_FILE_WITH_PATH))
debug_logger.debug("SUITE_RES_FILE_WITH_PATH : %s", str(SUITE_RES_FILE_WITH_PATH))
debug_logger.debug("SUITE_DEBUG_FILE_WITH_PATH : %s", str(SUITE_DEBUG_LOG_FILE_WITH_PATH))

debug_logger.debug("ROBOT_LOG_FILE_WITH_PATH : %s", str(ROBOT_LOG_FILE_WITH_PATH))
debug_logger.debug("ROBOT_REP_FILE_WITH_PATH : %s", str(ROBOT_REP_FILE_WITH_PATH))
debug_logger.debug("ROBOT_OUT_FILE_WITH_PATH : %s", str(ROBOT_OUT_FILE_WITH_PATH))
# ==========================================================================================================

# SonicAuto
SONICAUTO_CONN = "postgres://sonicauto:%s@10.203.15.9:5432/sonicauto" % parse.unquote('s0nicw@ll')
SONICAUTO_SESSION = sessionmaker(create_engine(SONICAUTO_CONN))

def get_sonicauto_session():
    debug_logger.debug("SONICAUTO CONN : %s", SONICAUTO_CONN)
    debug_logger.debug("SONICAUTO SESSION : %s ", SONICAUTO_SESSION)
    return SONICAUTO_SESSION()

# mail server
MAIL_SVR = '10.50.129.54'
DEFAULT_FROM_USER = 'auto_email@sonicwall.com'
DEFAULT_CC_USER = 'lnarayana@sonicwall.com'

# job related variables
try:
    QBS_JOBNUM = os.environ['QBS_JOBNUM']
    debug_logger.debug("QBS JOBNUM - using command : %s", str(QBS_JOBNUM))
except Exception as e:
    debug_logger.debug("QBS_JOBNUM ID Exception :" + str(e) + str(repr(e)))
    QBS_JOBNUM = '111111'
    debug_logger.debug("QBS JOBNUM - default : %s", str(QBS_JOBNUM))

# parameters
class Params:
    cc = ''
    scmlabel = ''
    testbed = ''
    avt_mountpoint = ''
    build = ''
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

###description for testcase and test stage which show in mail
class Descriptions:
    testcase = []
    teststage = []

class TestcaseLog:
    log = {}

# PythonRunner Home Dir
try:
    PYTHON_RUNNER_HOME = os.environ['PYTHON_RUNNER_HOME']
    debug_logger.debug("PYTHON RUNNER HOME - using command : %s", str(PYTHON_RUNNER_HOME))
except:
    PYTHON_RUNNER_HOME = '/SWIFT4.0/PythonRunner'
    debug_logger.debug("PYTHON RUNNER HOME - default : %s", str(PYTHON_RUNNER_HOME))

# Email templates
TEMPLATE_DIR = os.path.join(PYTHON_RUNNER_HOME, "winrunner/resources/templates/email")
debug_logger.debug(" TEMPLATE DIR : %s", str(TEMPLATE_DIR))
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
debug_logger.debug(" TEMPLATE ENV : %s", str(TEMPLATE_ENV))
TEST_COMPLETED_TEMPLATE = TEMPLATE_ENV.get_template("test_completed.html")
debug_logger.debug(" TEST COMPLETED TEMPLATE : %s", str(TEST_COMPLETED_TEMPLATE))

