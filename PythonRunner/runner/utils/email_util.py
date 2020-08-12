import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from runner.settings import MAIL_SVR, DEFAULT_FROM_USER, TEST_COMPLETED_TEMPLATE, START_TEST_COMPLETED_TEMPLATE
from runner.settings import logger


class SendMail:
    def __init__(self, to_users, cc_users=None):
        self.mail_srv = MAIL_SVR
        self.to_users = to_users
        self.cc_users = cc_users
        self.from_user = DEFAULT_FROM_USER
        if not self.from_user:
            self.from_user = 'auto_email@sonicwall.com'

    def start_mail(self, start_summary, dut_log, user):
        msg = MIMEMultipart('alternative')
        try:
            suite_name = start_summary['Testsuite Display Name']
            test_bed = start_summary['Test Bed']
            product = start_summary['Product']
            scmlabel = start_summary['Software Version']
            rgname = start_summary['rgname']
            subject = 'SonicTest: ' + rgname[rgname.find('['):rgname.find(']')+1] + suite_name + ': ' + test_bed + '- Test Started on Test Bed ' + test_bed
            start_summary.pop('rgname')

            msg['Subject'] = subject
            msg['From'] = self.from_user
            msg['To'] = self.to_users
            msg['Cc'] = self.cc_users

            full_html = START_TEST_COMPLETED_TEMPLATE.render(
                suite_name = suite_name,
                test_bed = test_bed,
                user = user,
                start_summary= start_summary,
                dut_log = dut_log,
            )
            html_display = MIMEText(full_html.encode('iso-8859-1'), 'html', 'iso-8859-1')
            msg.attach(html_display)
            send = smtplib.SMTP(self.mail_srv)
            # send.set_debuglevel(1)
            receiver = [self.to_users]
            if self.cc_users is not None:
                for i in self.cc_users.split(','):
                    receiver.append(i)
            send.sendmail(self.from_user, receiver, msg.as_string())
        except Exception as e:
            logger.info(e.args)
            logger.error('Fail to get ' + e.args)

    def finish_mail(self, res_summary, exec_summary, logs, test_details):
        msg = MIMEMultipart('alternative')

        try:
            # generate subject line
            suite_name = exec_summary['Testsuite Display Name']
            test_bed = exec_summary['Test Bed']
            product = exec_summary['Product']
            scmlabel = exec_summary['Software Version']
            rgname = exec_summary['rgname']
            result = 'PASSED: ' + res_summary[0]['Pass'] + ', FAILED: ' + res_summary[0]['Fail'] + ', SKIPPED: ' + res_summary[0]['Skip']
            if int(res_summary[0]['Fail']) > 0:
                color = 'PASSCODE:RED'
            elif int(res_summary[0]['Skip']) > 0:
                color = 'PASSCODE:YELLOW'
            else:
                color = 'PASSCODE:GREEN'

            subject = 'SonicTest: ' + rgname[rgname.find('['):rgname.find(']')+1] + suite_name + ': ' + test_bed + ' - Completed (' + color + ') for ' + product
            subject = subject + ': ' + result
            exec_summary.pop('rgname')

            msg['Subject'] = subject
            msg['From'] = self.from_user
            msg['To'] = self.to_users
            msg['Cc'] = self.cc_users
            full_html = TEST_COMPLETED_TEMPLATE.render(
                suite_name = suite_name,
                user = msg['To'],
                test_bed = test_bed,
                res_summary=res_summary,
                exec_summary = exec_summary,
                logs = logs,
                test_details = test_details
            )
            html_display = MIMEText(full_html.encode('utf-16'), 'html', 'utf-16')
            msg.attach(html_display)
            send = smtplib.SMTP(self.mail_srv)
            # send.set_debuglevel(1)
            receiver = [self.to_users]
            if self.cc_users is not None:
                for i in self.cc_users.split(','):
                    receiver.append(i)
            send.sendmail(self.from_user, receiver, msg.as_string())
        except Exception as e:
            logger.error(e.args)


# if __name__ == '__main__':
#     import os
#     print(os.path.dirname(__file__))
#     log = [
#         {'Name' : 'Test Command Log File', 'Link' : 'http://10.6.0.8/buildtestlogs/SONICCORE-VM/6.5.4.2-27v-12-464-d13abd80/VTB821/pzhou/pzhou_VTB821_1552887265/root_tqtest.pl_0/commands.log', 'Display':'commands.log'},
#         {'Name' : 'Test Command Line File', 'Link' :	'http://10.6.0.8/buildtestlogs/SONICCORE-VM/6.5.4.2-27v-12-464-d13abd80/VTB821/pzhou/pzhou_VTB821_1552887265/root_tqtest.pl_0/commands.log', 'Display':  'command_line.txt'},
#         {'Name' : 'TQTEST Log File', 'Link' : 'http://10.6.0.8/buildtestlogs/SONICCORE-VM/tqtest.log', 'Display' : 'tqtest.log'}
#         ]
#     test_summary= [
#         { 'Name' : 'NON Test Case Result', 'Pass' : '5', 'Fail' : '1', 'Error': '0'},
#         { 'Name' : 'Test Case Result', 'Pass' : '23', 'Fail' : '2', 'Error': '0'}
#         ]
#     Test_Exec_Summary    = {'Testsuite Display Name':'CDR3', 'Product' : '5600', 'Software Version' : '6.5.4.0-18n','Test Bed' : 'VTB726-PC1', 'Test Started at' : 'Thu Mar 14 19:09:42 2019', 'Test Finished at' : 'Thu Mar 14 19:12:13 2019'}
#     test_details = [
#         { 'type': 'NONTC', 'name': 'global.cfg', 'status' : 'passed', 'start_time' : '11:28:13', 'end_time': '11:29:31'},
#         { 'type': 'NONTC', 'name': 'get_firmware.cfg', 'status' : 'passed', 'start_time' : '11:31:43', 'end_time': '11:33:31'},
#         { 'type': 'NONTC', 'name': 'conf_testbed.cfg', 'status' : 'passed', 'start_time' : '11:34:13', 'end_time': '11:37:31'},
#         { 'type': 'TC', 'name': 'cdrouter1.cfg', 'status' : 'fail', 'start_time' : '11:38:13', 'end_time': '11:44:31'},
#         {'type': 'TC', 'name': 'cdrouter2.cfg', 'status': 'passed', 'start_time': '11:45:13', 'end_time': '11:49:31'}
#     ]
#     sm = SendMail({})
#     sm.finish_mail(test_summary, Test_Exec_Summary, log, test_details)
