import argparse
import csv
import datetime
import os
import subprocess
import re
from collections import OrderedDict
from winrunner.utils.log import log
from winrunner.utils.aptest import ApTest
from winrunner.utils.email_util import SendMail
from winrunner.utils.sonicauto import SonicAuto
from winrunner.settings import Params, LOGGING, DEBUG_LOGGING, SUITE_LOG_FILE_WITH_PATH, FAILED_SUITE_LOG_FILE_WITH_PATH, SUITE_RES_FILE_WITH_PATH, SUITE_LOG_FILE, FAILED_SUITE_LOG_FILE, SUITE_COMMAND_LINE_FILE, SUITE_COMMAND_LINE_FILE_WITH_PATH, Descriptions, TestcaseLog, debug_logger

logger = LOGGING.getLogger(__name__)

class Runner():
    def __init__(self, args, suite, to_users=None, cc_users=None):
        debug_logger.info("*** RUNNER BEGIN ***")
        # logger.info(args)
        debug_logger.debug("args :" + str(args))
        self.suite = suite
        self.suite_name = args[0]

        self.results = []
        self.has_uuid = False
        self.sa = SonicAuto()
        # debug_logger.debug("self.sa = SonicAuto() :" + self.sa)

        self.has_testcase_description = False
        self.has_stage_description = False

        debug_logger.debug("*** Params.total_pass *** :" + str(Params.total_pass))
        
        # process args that are not following the expected format
        temp_args = self._process_args(args[1:])
        debug_logger.debug("temp_args : " + str(temp_args))

        # parse test suite arguments
        parser = argparse.ArgumentParser(description="Parse test suite arguments")
        parser.add_argument('--g_cc', action="store", dest="cc", required=False)
        parser.add_argument('--g_scmlabel', action="store", dest="scmlabel")
        parser.add_argument('--g_testbed', action="store", dest="testbed", required=False)
        parser.add_argument('--g_avt_mountpoint', action="store", dest="avt_mountpoint", required=False)
        parser.add_argument('--g_build', action="store", dest="build", required=False)
        parser.add_argument('--g_product', action="store", dest="product")
        parser.add_argument('--g_user', action="store", dest="user")
        parser.add_argument('--g_requesttime', action="store", dest="requesttime")
        parser.add_argument('--mount_point', action="store", dest="mount_point", required=False)
        parser.add_argument('--g_qbs', action="store", dest="qbs", required=False)
        parser.add_argument('--g_resource', action="store", dest="resource", required=False)
        parser.add_argument('--bundle', action="store", dest="bundle", required=False)
        parser.add_argument('-rgname', action="store", dest="rgname", required=False)
        parser.add_argument('--g_openstack', action="store", dest="openstack", required=False)
        parser.add_argument('--setuptestbed', action="store", dest="setuptestbed", required=False)
        parser.add_argument('--setupjoblog', action="store", dest="setupjoblog", required=False)
        parser.add_argument('--g_openstack_tid', action="store", dest="openstack_tid", required=False)
        parser.add_argument('--starttime', action="store", dest="starttime", required=False)
        parser.add_argument('-log_level', action="store", dest="log_level", default='INFO', required=False)
        parser.add_argument('--log_dir', action="store", dest="log_dir", required=False)
        parser.add_argument('--g_version', action="store", dest="version", required=False)
        parser.add_argument('-sonicos_ver', action="store", dest="sonicos_ver", required=False)
        parser.add_argument('--trialrun', action="store_true", default=False, required=False)
        parser.add_argument('--no_database', action="store_true", default=False, required=False)
        parser.add_argument('--g_swvertype', action='store', dest='swvertype', required=False)
        parser.add_argument('-skip_dts', action="store_true", default=False, required=False)
        parser.add_argument('-dev', action="store_true", default=False, required=False)
        parser.add_argument('--g_qbs_jobnum', action="store", dest="qbs_jobnum")

        known, unkown = parser.parse_known_args(temp_args)
        logger.info(temp_args)
        logger.info(known)
        logger.info(unkown)
        debug_logger.info(" known arguments :" + str(known))
        debug_logger.info(" unknown arguments :" + str(unkown))
        val = vars(known)
        debug_logger.debug(" val :"+ str(val))
        logger.info(val)
        debug_logger.debug(" Params.total_pass :" + str(Params.total_pass))
        
        # save params to settings.Params
        Params.command = args
        debug_logger.debug(" Params.command-args :" + str(unkown))
        # temp_path = args[0].replace('\\', '/').replace('Y:', 'SWIFT4.0/TESTS')
        debug_logger.debug("Value of args[0] : " + str(args[0]))
        temp_path = args[0].replace('\\', '/').replace('Z:', 'SWIFT4.0')
        debug_logger.debug("Temp path before assigning to Params.path : " + str(temp_path))
        Params.path = "//depot/SQA/" + temp_path
        debug_logger.debug("Params.path :" + str(Params.path))

        if val['cc']: Params.cc = val['cc']
        if val['scmlabel']: Params.scmlabel = val['scmlabel']
        debug_logger.debug(" Inital value of Params.qbsjobid" + str(Params.qbsjobid))
        if val['qbs_jobnum']: Params.qbsjobid = val['qbs_jobnum']
        debug_logger.debug(" Final value of Params.qbsjobid after considering parameters" + str(Params.qbsjobid))
        if val['testbed']:
            debug_logger.debug("--- params testbed ---")
            logger.info(Params.testbed)
            Params.testbed = val['testbed'].upper()
            os.environ['G_TESTBED'] = val['testbed'].upper()
        if val['avt_mountpoint']: Params.avt_mountpoint = val['avt_mountpoint']
        if val['build']: Params.build = val['build']
        if val['product']: Params.product = val['product'].upper()
        if val['user']: Params.user = val['user']
        if val['requesttime']: Params.requesttime = val['requesttime']
        if val['mount_point']: Params.mount_point = val['mount_point']
        if val['qbs']: Params.qbs = val['qbs']
        if val['resource']: Params.resource = val['resource']
        if val['bundle']: Params.bundle = val['bundle']
        if val['rgname']: Params.rgname = val['rgname']
        if val['openstack']: 
            Params.openstack = val['openstack']
            os.environ['G_OPENSTACK'] = str(val['openstack'])
        if val['setuptestbed']: Params.setuptestbed = val['setuptestbed']
        if val['setupjoblog']: Params.setupjoblog = val['setupjoblog']
        if val['openstack_tid']: 
            Params.openstack_tid = val['openstack_tid']
            os.environ['G_OPENSTACK_TID'] = str(val['openstack_tid'])

        if val['starttime']:
            debug_logger.debug("--- starttime ---")
            Params.starttime = datetime.datetime.strptime(val['starttime'], '%Y-%m-%d %H:%M:%S')
        else:
            debug_logger.debug("--- starttime ---")
            Params.starttime = datetime.datetime.now().replace(microsecond=0)

        if val['log_level']: Params.log_level = val['log_level'].upper()
        if val['log_dir']: Params.log_dir = val['log_dir']
        if val['version']: Params.version = val['version']

        if val['dev']:
            os.environ["SONICOS_HOME"] = '/DEV_TESTS/SonicOS'
            os.environ["PYTHON_SONICOS_HOME"] = '/DEV_TESTS/python_SonicOS'
        if val['sonicos_ver']:
            Params.sonicos_ver = val['sonicos_ver']
            debug_logger.debug("Params.sonicos_ver : " + str(Params.sonicos_ver))
            ver_to_remove = val['sonicos_ver'] + "/"
            Params.path = Params.path.replace(ver_to_remove, "")
            debug_logger.debug("Params.path : " + str(Params.path))
            # os.environ["PYTHON_SONICOS_HOME"] = os.environ["PYTHON_SONICOS_HOME"] + '/' + Params.sonicos_ver
            os.environ["SONICOS_HOME"] = os.environ["SONICOS_HOME"] + '/' + Params.sonicos_ver
            
        if val['trialrun']: Params.trialrun = val['trialrun']
        if val['no_database']: Params.no_database = val['no_database']

        Params.requesttime = Params.requesttime.replace("_", " ")
        debug_logger.debug("Params.requesttime :" + str(Params.requesttime))

        Params.ts_actual_name = args[0].replace("/SWIFT4.0/TESTS/", "")
        debug_logger.debug("Params.ts_actual_name :" + str(Params.ts_actual_name))

        if Params.no_database or Params.trialrun:
            Params.db_upload = "No"

        if Params.testbed == '':
            debug_logger.debug(" Params.testbed  :" + str(Params.testbed))
            Params.testbed = os.uname()[1]

        # remove "-PC1" from the testbed name
        Params.testbed = Params.testbed.replace('-PC1','')

        # if no to_users passed in, send email to suite owner and user who submits the test
        if to_users is not None:
            tmp_to_users = to_users
        else:
            tmp_to_users = Params.user
            suite_owner = self.sa.get_testsuite_owner(Params.path)
            if suite_owner != '' and suite_owner != Params.user:
                tmp_to_users = tmp_to_users + "," + suite_owner

        self.to_users = self._process_users(tmp_to_users)

        # process cc_users
        if cc_users is not None:
            self.cc_users = self._process_users(cc_users)
        else:
            self.cc_users = None

        self._initiate_log()
        debug_logger.debug("*** RUNNER END ***")

    def _process_users(self, users):
        debug_logger.debug("users :" + str(users))
        user_list = re.split(r'[;,\s]\s*', users)
        debug_logger.debug("users :" + str(users))
        ret_list = []
        for u in user_list:
            if u.find('@') > 0:
                ret_list.append(u)
            else:
                ret_list.append(u + '@sonicwall.com')

        return ','.join(ret_list)

    def _process_args(self, args):
        args_str = ' '.join(args)
        debug_logger.debug("*** args for _process_args *** :" + str(args))
        return args_str.replace('-var ', '').replace('G_', '--g_').lower().replace('-rv ', '--').split(' ')

    def _initiate_log(self):
        # Write to CSV file
        output_file = open(SUITE_RES_FILE_WITH_PATH, 'w', newline='')
        debug_logger.debug("output_file :" + str(output_file))
        output_writer = csv.writer(output_file)
        output_writer.writerow(['ID', 'RESULT', 'STARTTIME', 'ENDTIME', 'UUID'])
        output_file.close()

        # command log file
        command_output_file = open(SUITE_COMMAND_LINE_FILE_WITH_PATH, 'w', newline='')
        print("command_output_file :" + str(command_output_file))
        command_output_file.write('python3 ' + ' '.join(Params.command))
        command_output_file.close()

        logger.info("Loaded suite :")
        debug_logger.info("Loaded suite")

    def run_and_parse_result(self):
        debug_logger.info(" *** In run and parse - testrunner.py ***")
        raise NotImplementedError

    def run(self):
        debug_logger.info("*** RUN-BEGIN ***")
        self.run_and_parse_result()
        debug_logger.info("*** RUN BEGIN 2 ***")
        self.parse_result_file()
        self.generate_failed_log()
        Params.finishtime = datetime.datetime.now().replace(microsecond=0)
        debug_logger.debug("Params.finishtime" + str(Params.finishtime))

        self.upload_result_to_sonicauto()
        debug_logger.debug("*** Upload to sonicauto end ***")
        if self.has_uuid and Params.qbsjobid != 'None':
            debug_logger.debug("*** self.has_uuid begin ***")
            logger.info("Will upload result to ApTest")
            debug_logger.info("Will upload result to ApTest")
            debug_logger.debug("*** QBSJOBID ***` :" + str(Params.qbsjobid))
            debug_logger.info("Will upload to ApTest")
            Params.total_aptest = self.upload_result_to_aptest()
            debug_logger.debug("Params.total_aptest :" + str(Params.total_aptest))
            debug_logger.debug("*** self.has_uuid end ***")
        self.send_email()
        debug_logger.info(" *** RUN END ***")

    def send_email(self):
        debug_logger.info("*** SEND MAIL BEGIN ***")
        sm = SendMail(self.to_users, self.cc_users)
        debug_logger.info("*** ONTO FINISH MAIL ***")
        sm.finish_mail(self.get_result_summary(), self.get_execution_summary(), self.get_logs_info(), self.results)
        debug_logger.info("*** SEND MAIL END ***")

    def upload_result_to_sonicauto(self):
        debug_logger.info("*** upload_result_to_sonicauto begin ***")
        self.sa.save_result(results=self.results)
        debug_logger.info("*** upload_result_to_sonicauto end ***")

    def upload_result_to_aptest(self):
        debug_logger.info("*** upload_result_to_aptest ***")
        ap = ApTest()
        debug_logger.info("ap (Aptest)" + str(ap))
        return ap.upload_aptest(self.results, Params.product, Params.scmlabel)

    def get_logs_info(self):
        debug_logger.info("*** GET LOG INFO BEGIN ***")
        data = []
        my_log = log(Params.resource, Params.product, Params.scmlabel, Params.testbed, Params.user)

        log_url = my_log.copy_file_to_log_server(SUITE_LOG_FILE_WITH_PATH)
        debug_logger.info("*** SUITE_LOG_FILE_WITH_PATH ***: " + SUITE_LOG_FILE_WITH_PATH)
        debug_logger.info("============ copy_file_to_log_server (failed log url) =============")
        failed_log_url = my_log.copy_file_to_log_server(FAILED_SUITE_LOG_FILE_WITH_PATH)
        debug_logger.info("============ copy_file_to_log_server (command log url) =============")
        command_log_url = my_log.copy_file_to_log_server(SUITE_COMMAND_LINE_FILE_WITH_PATH)
        debug_logger.info("============ copy_file_to_log_server 3 =============")
        debug_logger.debug("TYPE OF LOG URL" + str(type(log_url)))
        # print("LOG URL :", log_url)
        # print("FAILED LOG URL :", failed_log_url)
        # print("SUITE CMD LINE FILE :", command_log_url)

        data.append({
            'Name': 'Log File',
            'Link': str(log_url) + '/' + SUITE_LOG_FILE,
            'Display': SUITE_LOG_FILE
        })

        data.append({
            'Name': 'Failed Cases Log File',
            'Link': str(failed_log_url) + '/' + FAILED_SUITE_LOG_FILE,
            'Display': FAILED_SUITE_LOG_FILE
        })

        data.append({
            'Name': 'Command Line File',
            'Link': str(command_log_url) + '/' + SUITE_COMMAND_LINE_FILE,
            'Display': SUITE_COMMAND_LINE_FILE
        })

        console_url = my_log.get_dut_console_log_link()
        print("CONSOLE URL :", console_url)

        data.append({
            'Name': 'DUT Console Logs',
            'Link': console_url,
            'Display': 'console'
        })

        debug_logger.info("*** GET LOG INFO END ***")
        return data

    '''def get_mount_info(self):
        returned_value = subprocess.call()'''

    def get_execution_summary(self):
        mount_dev_tests = ""
        debug_logger.info("*** get execution summary begin ***")
        # query reg_total_exec, reg_exec_time, and display_name based on path
        debug_logger.debug("PARAMS.PATH : " + Params.path)
        mount_list = subprocess.Popen(["wmic", "logicaldisk", "get", "volumename,name"], stdout=subprocess.PIPE)
        mount_list = str(mount_list.communicate()[0]).replace(" ", "")
        mount_list = mount_list.replace(r'\r', '').split(r'\n')
        debug_logger.debug(" mount list : " + str(mount_list) + str(type(mount_list)))
        for i in mount_list:
            # if i.find('Perforce' or 'DEV_TESTS') != -1:
            if i.find('DEV_TESTS') != -1:
                debug_logger.debug(" required mount : " + i[:2])
                mount_dev_tests = i[:2]

        debug_logger.debug(" mount_dev_tests :" + mount_dev_tests)
        # ts_details = self.sa.get_testsuite_details(Params.path.replace("//depot/SQAY:\depot", r"Y:\depot"))
        ts_details = self.sa.get_testsuite_details(Params.path.replace("//depot/SQAY:", mount_dev_tests))
        debug_logger.info("*** params path replace *** :" + Params.path.replace("//depot/SQAY:", mount_dev_tests))
        Params.reg_total_exec = ts_details['testcases']
        Params.reg_exec_time = ts_details['exectime']
        Params.ts_display_name = ts_details['display_name']
        debug_logger.debug("Params.reg_total_exec " + str(Params.reg_total_exec))
        debug_logger.debug("Params.reg_exec_time " + str(Params.reg_exec_time))
        debug_logger.debug("Params.ts_display_name " + str(Params.ts_display_name))

        # calculate exec_time
        Params.exec_time = str(Params.finishtime - Params.starttime)
        Params.starttime = Params.starttime.strftime('%Y-%m-%d %H:%M:%S')
        Params.finishtime = Params.finishtime.strftime('%Y-%m-%d %H:%M:%S')
        debug_logger.debug("Params.exec_time " + str(Params.exec_time))
        debug_logger.debug("Params.starttime " + str(Params.starttime))
        debug_logger.debug("Params.finishtime" + str(Params.finishtime))

        data = OrderedDict()
        
        if Params.product and Params.product != '' : data['Product'] = Params.product
        if Params.scmlabel and Params.scmlabel != '': data['Software Version'] = Params.scmlabel
        if Params.testbed and Params.testbed != '': data['Test Bed'] = Params.testbed
        if Params.starttime and Params.starttime != '': data['Test Started at'] = Params.starttime
        if Params.finishtime and Params.finishtime != '': data['Test Finished at'] = Params.finishtime
        if Params.reg_exec_time and Params.reg_exec_time != 0: data['Registered Execution Time'] = Params.reg_exec_time
        if Params.exec_time and Params.exec_time != 0: data['Actual Execution Time'] = Params.exec_time
        if Params.reg_total_exec and Params.reg_total_exec != 0: data['Registered Total Testcases'] = Params.reg_total_exec
        if Params.total_exec and Params.total_exec != 0: data['Actual Testcases Executed'] = Params.total_exec
        if Params.total_aptest and Params.total_aptest != 0: data['Results Uploaded to APTEST'] = Params.total_aptest
        if Params.ts_actual_name and Params.ts_actual_name != '': data['Testsuite Actual Name'] = Params.ts_actual_name
        if Params.ts_display_name and Params.ts_display_name != '': data['Testsuite Display Name'] = Params.ts_display_name
        if Params.log_location and Params.log_location != '': data['Local Log Dir'] = Params.log_location
        if Params.qbsjobid and Params.qbsjobid != '': data['QBS Job ID'] = Params.qbsjobid
        if Params.db_upload: data['Database Upload'] = Params.db_upload
        if Params.setuptestbed and Params.setuptestbed != '': data['OpenStack Setup Test Bed'] = Params.setuptestbed
        if Params.setupjoblog and Params.setupjoblog != '': data['OpenStack Setup Job Log'] = Params.setupjoblog

        debug_logger.info("*** Get execution summary end ***")
        return data

    def get_result_summary(self):
        debug_logger.info("*** Get result summary begin ***")
        debug_logger.info("*** self.results *** :" + str(self.results))
        debug_logger.info("*** Params.totalpass INITIAL :*** :" + str(Params.total_pass))
        debug_logger.info("*** Params.total_fail INITIAL : *** :" + str(Params.total_failures))
        debug_logger.info("*** Params.total_errors INITIAL :*** :" + str(Params.total_errors))
        debug_logger.info("*** Params.total_skip INITIAL :*** :" + str(Params.total_skip))
        for result in self.results:
            if result['uuid'] == 'NonTC':
                if result['result'].upper() == 'PASSED': Params.nontc_total_pass += 1 
                if result['result'].upper() == 'FAILED': Params.nontc_total_failures += 1 
                if result['result'].upper() == 'ERROR': Params.nontc_total_errors += 1 
                if result['result'].upper() == 'SKIP': Params.nontc_total_skip += 1 
                Params.nontc_total_run += 1
            else:
                if result['result'].upper() == 'PASSED': Params.total_pass += 1
                if result['result'].upper() == 'FAILED': Params.total_failures += 1 
                if result['result'].upper() == 'ERROR': Params.total_errors += 1 
                if result['result'].upper() == 'SKIP': Params.total_skip += 1 
                # Params.total_run += 1
                debug_logger.info("*** Params.total run ***" + str(Params.total_run))
                debug_logger.info("*** Params.total pass ***" + str(Params.total_pass))
                Params.total_run = str(int(Params.total_run) + 1)
                debug_logger.info("*** params.total_run *** :" + str(Params.total_run))

        debug_logger.info("*** Params.totalpass FINAL :*** :" + str(Params.total_pass))
        debug_logger.info("*** Params.total_fail FINAL : *** :" + str(Params.total_failures))
        debug_logger.info("*** Params.total_errors FINAL :*** :" + str(Params.total_errors))
        debug_logger.info("*** Params.total_skip FINAL :*** :" + str(Params.total_skip))
        res_summary = [{
            'Name': 'Test Case Result',
            'Pass': str(Params.total_pass),
            'Fail': str(Params.total_failures),
            # 'Error': str(Params.total_errors)
            'Skip': str(Params.total_skip)
        },
            {
            'Name': 'Non Test Case Result',
            'Pass': str(Params.nontc_total_pass),
            'Fail': str(Params.nontc_total_failures),
            # 'Error': str(Params.nontc_total_errors)
            'Skip': str(Params.nontc_total_skip)
        }
        ]
        debug_logger.info(" *** result summary *** :" + str(res_summary))
        debug_logger.info(" *** Get result summary end ***")
        return res_summary

    def parse_result_file(self):
        debug_logger.info("*** PARSE RESULT FILE BEGIN ***")
        # TEMP_SUITE_RES_FILE_WITH_PATH = r"X:\testfiles\WAF\CSV\authentication_ts_VTB146.csv"
        debug_logger.info("self.result2 -- SUITE_RES_FILE_WITH_PATH" + str(SUITE_RES_FILE_WITH_PATH))
        # print("self.result2 -- TEMP_SUITE_RES_FILE_WITH_PATH", TEMP_SUITE_RES_FILE_WITH_PATH)
        with open(SUITE_RES_FILE_WITH_PATH, 'r') as result_file:
            debug_logger.info("*** result file *** :" + str(result_file))
            reader = csv.DictReader(result_file)
            # reader = csv.DictReader(SUITE_RES_FILE_WITH_PATH)
            '''f4 = open(SUITE_RES_FILE_WITH_PATH, 'r')
            with f4:
                reader = csv.DictReader(f4)
                print("*** reader2 - int ***", reader)
                for row in reader:
                    print("row element : ")
                    print(row['ID'], row['RESULT'], row['STARTTIME'], row['ENDTIME'], row['UUID'])
                    # for e in row:
                        # print("row element :", e)
            # f4.close()
            print("*** reader3 ***", reader)'''
            for row in reader:
                debug_logger.info("*** in reader ***")
                debug_logger.info("*** the row *** : " + str(row))
                type = 'NonTC' if row['UUID'] == 'NonTC' or None else 'TestCase'

                self.results.append({
                    # 'title': row['ID'],
                    'title': '', #this key is for mouseover testcase name in mail
                    'result': row['RESULT'],
                    'starttime': row['STARTTIME'],
                    'endtime': row['ENDTIME'],
                    'uuid': row['UUID'],
                    'matrixid': 0,
                    'type': type,
                    'parameters': '',
                    'alias': '',
                    # 'filename': self.suite_name,
                    'filename':  row['ID'],
                    'log_link': '',
                    'failed_stage': [], #print these stage when a testcase failed
                })
                debug_logger.debug("self.result.append : " + str(self.results))
                if not self.has_uuid and (row['UUID'] is not None and row['UUID'] != 'NonTC'):
                    self.has_uuid = True
                '''
                [{'title': 'Verify Web requests are forwarded to a Proxy Server located on the WAN', 'result': 'FAILED', 'starttime': '2019-10-22 18:23:19', 'endtime': '2019-10-22 18:23:35', 'uuid': 'B226210E-0464-11DE-860E-445A00F93527', 'matrixid': 0, 'type': 'TestCase', 'parameters': '', 'alias': '', 'filename': 'TestWebproxy_02', 'log_link': '', 'failed_stage': ['test_02_02_start_http_connectionfailed']}, {'title': 'Verify that the firewall will accept only valid port number in the Web Proxy configuration page', 'result': 'PASSED', 'starttime': '2019-10-22 18:23:35', 'endtime': '2019-10-22 18:24:53', 'uuid': 'B23B1212-0464-11DE-860E-445A00F93527', 'matrixid': 0, 'type': 'TestCase', 'parameters': '', 'alias': '', 'filename': 'TestWebproxy_01', 'log_link': '', 'failed_stage': []}]
                '''
                for failed_stages in Descriptions.teststage:
                    if row['ID'] in failed_stages.keys():
                        for failed_stage in failed_stages[row['ID']]:
                            self.results[-1]['failed_stage'].append(failed_stage + ': ' + failed_stages[row['ID']][failed_stage])
                        break
                for description in Descriptions.testcase:
                    if row['ID'] in description.keys():
                        self.results[-1]['title'] = description[row['ID']]
                        break
                my_log = log(Params.resource, Params.product, Params.scmlabel, Params.testbed, Params.user)
                debug_logger.info("*** log call done ***")
                self.results[-1]['log_link'] = str(my_log.copy_file_to_log_server(TestcaseLog.log[row['ID']])) + os.path.split(TestcaseLog.log[row['ID']])[1]
                debug_logger.info("*** TestcaseLog.log[row['ID']] *** :" + str(TestcaseLog.log[row['ID']]))
                debug_logger.info("*** os.path.split(TestcaseLog.log[row['ID']])[1] *** :" + str(os.path.split(TestcaseLog.log[row['ID']])[1]))
                debug_logger.info("*** self.results *** :" + str(self.results))
                debug_logger.info("*** self.results[-1]['log_link'] *** : " + str(self.results[-1]['log_link']))
                # f4.close()
                debug_logger.info("*** PARSE RESULT FILE END ***")
                
    def generate_failed_log(self):
        debug_logger.info("*** GENERATE FAILED LOG BEGIN ***")
        output_file = open(FAILED_SUITE_LOG_FILE_WITH_PATH, 'a')
        debug_logger.debug("FAILED_SUITE_LOG_FILE_WITH_PATH" + str(FAILED_SUITE_LOG_FILE_WITH_PATH))
        # csv_log = open(SUITE_RES_FILE_WITH_PATH).read()
        output_file.write(self.csv2log(SUITE_RES_FILE_WITH_PATH))
        output_file.write('\n'*3)
        output_file.write(self.fetch_failed_log())
        debug_logger.info("*** GENERATE FAILED LOG END ***")

    def fetch_failed_log(self):
        failed_log = ''
        debug_logger.debug("fetch-failed-log : SUITE_LOG_FILE_WITH_PATH " + str(SUITE_LOG_FILE_WITH_PATH))
        total_log = open(SUITE_LOG_FILE_WITH_PATH).read()
        start = '########## STARTING CASE:'
        end = '########## Testcase.*?##########'
        pattern = re.compile(('\[.*?\] \[.*?\] - ' + start+'.*?' + end), re.S)
        debug_logger.debug("fetch-failed-log : Pattern " + str(pattern))
        results = pattern.findall(total_log)
        debug_logger.debug("fetch-failed-log : results " + str(results))
        for result in results:
            if re.search('FAILED  ##########', result, re.I):
                failed_log += result
        return failed_log + '\n'
                
    def csv2log(self, file):
        csv = open(file)
        width1 = 60
        width2 = 48
        log = 'Complete TestSuite : ' + os.path.basename(self.suite_name) 
        log += '\n' + '='*len(log) + '\n'*2
        log += 'Testcase'.center(width1, ' ') + 'Status'.ljust(width2, ' ') + '\n'
        log += ''.center(width1+width2, '-') + '\n'
        print("csv-log : ", log)
        for line in csv:
            (id, result, starttime, endtime, uuid) = line.split(',')
            if id == 'ID':
                continue
            log += id.ljust(width1, '-') + (result + ' ' + starttime + ' ' + endtime).ljust(width2, ' ') + '\n'
        return log