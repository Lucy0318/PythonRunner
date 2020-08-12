import argparse
import csv
import datetime
import os
import re
import time
import platform
import sys
import subprocess
from collections import OrderedDict
from runner.utils.log import log
from runner.utils.aptest import ApTest
from runner.utils.email_util import SendMail
from runner.utils.sonicauto import SonicAuto
from runner.settings import Params, logger,python_logger, SUITE_LOG_FILE_WITH_PATH, FAILED_SUITE_LOG_FILE_WITH_PATH, SUITE_RES_FILE,SUITE_RES_FILE_WITH_PATH, SUITE_PYTHON_FILE_WITH_PATH, SUITE_PYTHON_FILE, SUITE_LOG_FILE, FAILED_SUITE_LOG_FILE, SUITE_COMMAND_LINE_FILE, SUITE_COMMAND_LINE_FILE_WITH_PATH, Descriptions, TestcaseLog, TIMESTAMP, LOG_DIR


class Runner():
    def __init__(self, args, suite, to_users=None, cc_users=None):
        self.suite = suite
        self.suite_name = args[0]

        self.results = []
        self.has_uuid = False
        self.sa = SonicAuto()

        # if no to_users passed in, send email to suite owner and user who submits the test
        if to_users is not None:
            tmp_to_users = to_users
        else:
            tmp_to_users = Params.user
            suite_owner = self.sa.get_testsuite_owner(Params.path)
            if suite_owner != '' and suite_owner != Params.user:
                tmp_to_users = tmp_to_users + "," + suite_owner['name']

        self.to_users = self._process_users(tmp_to_users)

        # process cc_users
        if cc_users is not None:
            self.cc_users = self._process_users(cc_users)
            self.cc_users = self.cc_users + ',automation@sonicwall.com,shanghai_automation@sonicwall.com'
        else:
            self.cc_users = "automation@sonicwall.com,shanghai_automation@sonicwall.com"
        if Params.cc:
            self.cc_users = self._process_users(Params.cc) + ',' + self.cc_users
        self.cmd_line = 'python3 ' + ' '.join(Params.command)
        self._initiate_log()

    def _process_users(self, users):
        user_list = re.split(r'[;,\s]\s*', users)
        ret_list = []
        for u in user_list:
            if u:
                if u.find('@') > 0:
                    ret_list.append(u)
                else:
                    ret_list.append(u + '@sonicwall.com')

        return ','.join(ret_list)

    def _initiate_log(self):
        self._initiate_python_log()
        output_file = open(SUITE_RES_FILE_WITH_PATH, 'w', newline='')
        output_writer = csv.writer(output_file)
        output_writer.writerow(['ID', 'RESULT', 'STARTTIME', 'ENDTIME', 'UUID'])
        output_file.close()
        command_output_file = open(SUITE_COMMAND_LINE_FILE_WITH_PATH, 'w', newline='')
        command_output_file.write(self.cmd_line)
        command_output_file.close()

        logger.info("Loaded suite")

    def _initiate_python_log(self):
        python_logger.write('Dumping ENV:'+ '\n')
        for env in os.environ:
            python_logger.write(' '*8 +env + '= ' + os.environ[env] + '\n')
        python_logger.write('Start time: ' + TIMESTAMP + '\n')
        python_logger.write('Command line: ' + self.cmd_line+ '\n')
        python_logger.write('Test log dir: ' + LOG_DIR+ '\n')
        if re.search(r'Linux', platform.system(), re.I):
            python_logger.write('Route table:' + str(subprocess.Popen(['route'] + ['-n'], stdout=subprocess.PIPE).communicate()[0],encoding="utf8")+ '\n')
            python_logger.write('DNS setting:' + str(subprocess.Popen(['cat'] + ['/etc/resolv.conf'], stdout=subprocess.PIPE).communicate()[0],encoding="utf8")+ '\n')
        elif re.search(r'cygwin|mswin32', platform.system(), re.I):
            python_logger.write('Route table:' + str(subprocess.Popen(['/cygdrive/c/WINDOWS/system32/route'] + ['print'], stdout=subprocess.PIPE).communicate()[0],encoding="utf8")+ '\n')
            python_logger.write('DNS setting:' + str(subprocess.Popen(['/cygdrive/c/WINDOWS/system32/ipconfig'] + ['/all'], stdout=subprocess.PIPE).communicate()[0],encoding="utf8")+ '\n')
        if Params.sonicos_ver:
            sys.path.append(os.environ["PYTHON_COMMON_HOME"])
            from util.openstack import Openstack
            try:
                if Params.testbed and Params.openstack and int(Params.openstack) == 1:
                    ostack = Openstack(Params.testbed)
                    nodes = ostack.get_nodes()
                    python_logger.write('OpenStack Topology Definition: \n')
                for node in nodes:
                    python_logger.write(' '*4 + '{\n')
                    for node_key in node:
                        python_logger.write(' '*8 + node_key + '=> ' + str(node[node_key]) + '\n')
                    python_logger.write(' '*4 + '}\n\n')
            except Exception as e:
                logger.error(e.args)

    def run_and_parse_result(self):
        raise NotImplementedError

    def run(self):
        self.send_start_email()
        self.run_and_parse_result()
        self.parse_result_file()
        self.generate_failed_log()
        Params.finishtime = datetime.datetime.now().replace(microsecond=0)

        self.upload_result_to_sonicauto()
        if self.has_uuid and Params.qbsjobid != 'None':
            logger.info("Will upload result to ApTest")
            Params.total_aptest = self.upload_result_to_aptest()
        self.postrun()
        self.send_email()

    def postrun(self):
        python_logger.write('\nExiting Testsuite...\n\n')
        python_logger.flush()

    def send_email(self):
        sm = SendMail(self.to_users, self.cc_users)
        sm.finish_mail(self.get_result_summary(), self.get_execution_summary(), self.get_logs_info(), self.results)

    def send_start_email(self):
        sm = SendMail(self.to_users, self.cc_users)
        sm.start_mail(self.get_start_summary(), self.get_dut_log(), self.sa.get_full_name(Params.user)['full_name'])

    def upload_result_to_sonicauto(self):
        for i in range(0,5):
            result = self.sa.save_result(results=self.results)
            if result == 'Result got saved successfully':
                break
            time.sleep(5)
            logger.info('Try again to upload result to sonicauto...')
            self.sa = SonicAuto()

    def upload_result_to_aptest(self):
        ap = ApTest()
        return ap.upload_aptest(self.results, Params.product, Params.scmlabel)

    def get_dut_log(self):
        data = {
            'Name': 'DUT Console Logs',
            'Link': '',
            'Display': '',           
        }
        try:
            my_log = log(Params.resource, Params.product, Params.scmlabel, Params.testbed, Params.user)
            console_url = my_log.get_dut_console_log_link()
             
            data['Link'] = console_url[0]
            data['Display'] = console_url[0].split('/')[-1]
        except:
            logger.error("Unable to get DUT console info.")
        return data

    def get_logs_info(self):
        data = []
        my_log = log(Params.resource, Params.product, Params.scmlabel, Params.testbed, Params.user)

        my_log.copy_file_to_log_server(LOG_DIR)
        data.append({
            'Name': 'Log File',
            'Link': my_log.uploaddir_url + SUITE_LOG_FILE,
            'Display': SUITE_LOG_FILE
        })

        data.append({
            'Name': 'Failed Cases Log File',
            'Link': my_log.uploaddir_url + FAILED_SUITE_LOG_FILE,
            'Display': FAILED_SUITE_LOG_FILE
        })

        data.append({
            'Name': 'Command Line File',
            'Link': my_log.uploaddir_url + SUITE_COMMAND_LINE_FILE,
            'Display': SUITE_COMMAND_LINE_FILE
        })

        data.append({
            'Name': 'PythonRunner File',
            'Link': my_log.uploaddir_url + SUITE_PYTHON_FILE,
            'Display': SUITE_PYTHON_FILE
        })

        try:
            console_url = my_log.get_dut_console_log_link()

            data.append({
                'Name': 'DUT Console Logs',
                'Link': console_url[0],
                'Display': console_url[0].split('/')[-1]
            })
        except:
            data.append({
                'Name': 'DUT Console Logs',
                'Link': '',
                'Display': '',
            })            

        return data

    def get_start_summary(self):
        ts_details = self.sa.get_testsuite_details(Params.path)
        Params.ts_display_name = ts_details['display_name']

        data = OrderedDict()
        data['rgname'] = Params.rgname
        # if Params.ts_display_name and Params.ts_actual_name != '': data['Testsuite Display Name'] = Params.ts_actual_name
        if Params.ts_display_name and Params.ts_display_name != '': data['Testsuite Display Name'] = Params.ts_display_name
        if Params.product and Params.product != '' : data['Product'] = Params.product
        if Params.scmlabel and Params.scmlabel != '': data['Software Version'] = Params.scmlabel
        if Params.testbed and Params.testbed != '': data['Test Bed'] = Params.testbed
        if Params.starttime and Params.starttime != '': data['Test Started at'] = Params.starttime
        if Params.qbsjobid and Params.qbsjobid != '': data['QBS Job ID'] = Params.qbsjobid
        if Params.setuptestbed and Params.setuptestbed != '': data['OpenStack Setup Test Bed'] = Params.setuptestbed
        if Params.setupjoblog and Params.setupjoblog != '': data['OpenStack Setup Job Log'] = Params.setupjoblog
        return data

    def get_execution_summary(self):
        # query reg_total_exec, reg_exec_time, and display_name based on path
        ts_details = self.sa.get_testsuite_details(Params.path)
        Params.reg_total_exec = ts_details['testcases']
        Params.reg_exec_time = ts_details['exectime']
        Params.ts_display_name = ts_details['display_name']

        # calculate exec_time
        Params.exec_time = str(Params.finishtime - Params.starttime)
        Params.starttime = Params.starttime.strftime('%Y-%m-%d %H:%M:%S')
        Params.finishtime = Params.finishtime.strftime('%Y-%m-%d %H:%M:%S')

        data = OrderedDict()
        
        data['rgname'] = Params.rgname
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

        return data

    def get_result_summary(self):
        for result in self.results:
            if result['uuid'] == 'NonTC':
                if result['result'].upper() == 'PASSED': Params.nontc_total_pass += 1 
                if result['result'].upper() == 'FAILED': Params.nontc_total_failures += 1 
                if result['result'].upper() == 'ERROR': Params.nontc_total_failures += 1 
                if result['result'].upper() == 'SKIP': Params.nontc_total_skip += 1 
                Params.nontc_total_run += 1
            else:
                if result['result'].upper() == 'PASSED': Params.total_pass += 1 
                if result['result'].upper() == 'FAILED': Params.total_failures += 1 
                if result['result'].upper() == 'ERROR': Params.nontc_total_failures += 1 
                if result['result'].upper() == 'SKIP': Params.total_skip += 1 
                Params.total_run += 1  
        res_summary = [{
            'Name': 'Test Case Result',
            'Pass': str(Params.total_pass),
            'Fail': str(Params.total_failures),
#            'Error': str(Params.total_errors)
            'Skip': str(Params.total_skip)
        },
        {
            'Name': 'Non Test Case Result',
            'Pass': str(Params.nontc_total_pass),
            'Fail': str(Params.nontc_total_failures),
#            'Error': str(Params.nontc_total_errors)
            'Skip': str(Params.nontc_total_skip)
        }
        ]
        return res_summary

    def parse_result_file(self):
        with open(SUITE_RES_FILE_WITH_PATH,'r') as result_file:
            reader = csv.DictReader(result_file)
            for row in reader:
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
                    'ftype': '',
                    'parameters': '',
                    'alias': '',
                    # 'filename': self.suite_name,
                    'filename':  row['ID'],
                    'log_link': '',
                    'dts_jira_link': '',
                    'failed_stage': [], #print these stage when a testcase failed
                })

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

                self.results[-1]['log_link'] = my_log.uploaddir_url + TestcaseLog.log[row['ID']]
                self.results[-1]['dts_jira_link'] = Params.dts_jira_link[row['ID']]
                if Params.trialrun:
                    self.results[-1]['ftype'] = 'TrialRun'
                elif self.results[-1]['dts_jira_link']:
                    self.results[-1]['ftype'] = 'Software'
                else:
                    self.results[-1]['ftype'] = 'Uncategorized'

    def generate_failed_log(self):
        output_file = open(FAILED_SUITE_LOG_FILE_WITH_PATH, 'a')
        output_file.write(self.csv2log(SUITE_RES_FILE_WITH_PATH))
        output_file.write('\n'*3)
        output_file.write(self.fetch_failed_log())        

    def fetch_failed_log(self):
        failed_log = 'Failed Testcase Detailed Log'.center(108, '*') + '\n'*2
        total_log = open(SUITE_LOG_FILE_WITH_PATH).read()
        start = '########## STARTING CASE:'
        end = '########## Testcase.*?##########'
        pattern = re.compile(('\[.*?\] \[.*?\] - ' + start+'.*?' + end), re.S)
        results = pattern.findall(total_log)
        for result in results:
            if re.search('FAILED  ##########', result, re.I):
                failed_log += result + '\n'
        return failed_log + '\n'
                
    def csv2log(self, file):
        csv = open(file)
        width1 = 60
        width2 = 48
        log = 'Complete TestSuite : ' + os.path.basename(self.suite_name) 
        log += '\n' + '='*len(log) + '\n'*2
        log += 'Testcase'.center(width1, ' ') + 'Status'.ljust(width2, ' ') + '\n'
        log += ''.center(width1+width2, '-') + '\n'
        for line in csv:
            (id, result, starttime, endtime, uuid) = line.split(',')
            if id == 'ID':
                continue
            log += id.ljust(width1, '-') + (result + ' ' + starttime + ' ' + endtime).ljust(width2, ' ') + '\n'
        return log

    def __del__(self):
        print('Your Logs are in ' + LOG_DIR)
        python_logger.close()
