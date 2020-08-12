import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from winrunner.settings import MAIL_SVR, DEFAULT_FROM_USER, TEST_COMPLETED_TEMPLATE
from winrunner.settings import LOGGING

logger = LOGGING.getLogger(__name__)


class SendMail:
    def __init__(self, to_users, cc_users=None):
        self.mail_srv = MAIL_SVR
        self.to_users = to_users
        self.cc_users = cc_users
        self.from_user = DEFAULT_FROM_USER
        print("MAIL_SVR :", MAIL_SVR)
        print("to_users :", to_users)
        print("cc_users :", cc_users)
        print("DEFAULT_FROM_USER2 :", DEFAULT_FROM_USER)

    def finish_mail(self, res_summary, exec_summary, logs, test_details):
        print("............ Finish Mail Start..........")
        print("Result Summary : ", res_summary)
        msg = MIMEMultipart('alternative')

        try:
            # generate subject line
            print("-- Try block --")
            print("EXEC SUMMARY : ", exec_summary)
            suite_name = exec_summary['Testsuite Display Name']
            test_bed = exec_summary['Test Bed']
            product = exec_summary['Product']
            # product = 'NSA'
            scmlabel = exec_summary['Software Version']
            # scmlabel = '6.5.4'
            print("~~~ STAGE 4 : result info ~~~~")
            # result = 'PASSED: ' + res_summary[0]['Pass'] + ', FAILED: ' + res_summary[0]['Fail'] + ', Errors: ' + res_summary[0]['Error']
            result = 'PASSED: ' + res_summary[0]['Pass'] + ', FAILED: ' + res_summary[0]['Fail'] + ', Skipped: ' + res_summary[0]['Skip']
            print("email_result :", result)
            if int(res_summary[0]['Fail']) > 0:
                color = 'PASSCODE:GREEN'
            elif int(res_summary[0]['Skip']) > 0:
                color = 'PASSCODE:YELLOW'
            else:
                color = 'PASSCODE:GREEN'

            subject = 'SonicTest: ' + suite_name + ': ' + test_bed + ' - Completed (' + color + ') for ' + product
            subject = subject + ': ' + result
            print("mail subject :", subject)

            msg['Subject'] = subject
            msg['From'] = self.from_user
            msg['To'] = self.to_users
            msg['Cc'] = self.cc_users
            full_html = TEST_COMPLETED_TEMPLATE.render(
                suite_name = suite_name,
                test_bed = test_bed,
                res_summary=res_summary,
                exec_summary = exec_summary,
                logs = logs,
                test_details = test_details
            )

            print("======= email_util : full html part executed ===========")
            print("test details : ", test_details)
            print("~~~~~~~test details [0] ~~~~~~~~~~~ :", test_details[0])
            # print("~~~~~~~test details [1] ~~~~~~~~~~~ :", test_details[1])
            # f3 = open(r"C:\Users\trial.txt", "w+")
            # f3.write(full_html)
            # f3.close()
            html_display = MIMEText(full_html.encode('iso-8859-1'), 'html', 'iso-8859-1')
            msg.attach(html_display)
            send = smtplib.SMTP(self.mail_srv)
            send.set_debuglevel(1)
            receiver = [self.to_users]
            if self.cc_users is not None:
                for i in self.cc_users.split(','):
                    receiver.append(i)
            print("==== mail successful =====")
            send.sendmail(self.from_user, receiver, msg.as_string())
        except Exception as e:
            print("===== error logged =======")
            print("EXCEPTION mail:", e)
            logger.error(e.args)

        print("............ Finish Mail End..........")


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
