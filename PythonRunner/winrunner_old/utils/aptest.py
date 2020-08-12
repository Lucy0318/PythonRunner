import subprocess
import time
from winrunner.utils.sonicauto import SonicAuto
from winrunner.settings import LOGGING

logger = LOGGING.getLogger(__name__)


class UploadAptestException(Exception):
    def __init__(self, info):
        print("Upload Aptest INFO :", info)
        super().__init__(f"Upload result to ApTest is skipped: {info}")


class ApTest:
    def __init__(self, host='10.208.1.8', token='qatoken', user_name='automation', retry=5):
        self.host = host
        self.token = token
        self.user_name = user_name
        self.retry = retry
        self.uuid_map = {}

    def upload_aptest(self, results, platform, scmlabel):
        num_of_case_uploaded = 0

        try:
            # get session_group_id
            sa = SonicAuto()
            product_id = str(sa.get_product_id_from_platform(platform))
            if product_id == 0:
                raise UploadAptestException("product id is not found")

            session_group_id = sa.get_session_group_name(scmlabel, product_id)
            if session_group_id == '':
                raise UploadAptestException("session group id is not found")

            # get ApTest suite name from product_name
            application_platform_aptest_mapping = {
                'GMS': 'GMSVP',
                'LICENSEMANAGER': 'License_Manager',
                'MYSONICWALL': 'Latte',
                'SANDBOX': 'Latte',
                'SNOWSHOE': 'Latte',
                'CFC': 'Desktop_Clients'
            }

            productid_aptest_mapping = {
                '2': 'SMA_1000_AO_Phase-6',
                '3': 'EmailSecurity',
                '5': 'SMA_100_AO_Phase6',
                '6': 'firmware_sonicos',
                '7': 'wxa',
                '8': 'Web_Application_Firewall',
                '9': 'SMA_1000_AO_Phase-6',
                '10': 'CloudWAF',
                '11': 'Capture_Client',
                '12': 'Latte'
            }

            aptest_suite_name = ''
            if product_id == '1':
                aptest_suite_name = application_platform_aptest_mapping[platform]
            else:
                aptest_suite_name = productid_aptest_mapping[product_id]

            retry = self.retry
            while (retry):
                if self.get_session_numbers_from_group_id(aptest_suite_name, session_group_id):
                    retry -= 1
                    time.sleep(20)
                else:
                    break

            for tc in results:
                if not 'uuid' in tc:
                    logger.warning("INFO: Testcase uuid not defined.  Results not uploaded to ApTest")
                    continue

                uuid = tc['uuid']
                if uuid in self.uuid_map:
                    session_number = self.uuid_map[uuid]
                    if self.update_results(scmlabel, platform, aptest_suite_name, session_number, **tc) == '0':
                        num_of_case_uploaded += 1
        except UploadAptestException as e:
            print("------- EXCEPTION -------- :", e)
            logger.warning(e.args)
        except Exception as e:
            logger.warning(e.args)

        return num_of_case_uploaded

    def get_session_numbers_from_group_id(self, aptest_suite_name, session_group_id):
        rpc_query_string = '?suite=' + aptest_suite_name + '&sessiongroupid=' + session_group_id

        rpc_url = 'https://' + self.host + '/sw-getSessionsWithVar.pl' + rpc_query_string
        logger.info("DEBUG: RPC URL is: " + rpc_url)
        params = ['--connect-timeout', '20', '--silent', '-k']
        params.append(rpc_url)

        try:
            rpc_result_string = subprocess.Popen(['curl'] + params, stdout=subprocess.PIPE).communicate()[0]
            return_string = rpc_result_string.decode('ASCII')
            rpc_result_list = return_string.split('\n')

            rpc_return_value = rpc_result_list.pop(0)
            logger.info("DEBUG: RPC result value is: " + rpc_return_value)

            for session_setname in rpc_result_list:
                if session_setname == '':
                    continue
                session_number, set_name = session_setname.split(',')

                rpc_query_string = '?suite=' + aptest_suite_name + '&set=' + set_name + '&session=' + session_number

                rpc_url = 'https://' + self.host + '/sw-autotclist.pl' + rpc_query_string
                logger.info("DEBUG: RPC URL is: " + rpc_url)
                params = ['--connect-timeout', '20', '--silent', '-k']
                params.append(rpc_url)

                rpc_result_string = subprocess.Popen(['curl'] + params, stdout=subprocess.PIPE).communicate()[0]
                return_string = rpc_result_string.decode('ASCII')
                rpc_result_list_uuid = return_string.split('\n')

                rpc_return_code = rpc_result_list_uuid.pop(0)
                logger.info("DEBUG: TC list result code is: " + rpc_return_code)

                if rpc_return_code == 1:
                    logger.info("Failed return status from getUUIDsFromSessionNumber")
                elif len(rpc_result_list_uuid) == 1:
                    logger.info("No corresponding testcases for the given session number")
                else:
                    for testcase_data in rpc_result_list_uuid:
                        uuid = testcase_data.split(',')
                        self.uuid_map[uuid[0]] = session_number

        except:
            logger.error("Unable to run rpc query")
            return 1

    def update_results(self, scmlabel, platform, aptest_suite_name, session_number, **tc):
        uuid = tc['uuid']

        result = ''
        if 'result' in tc:
            result = tc['result']
        note = ''
        if 'note' in tc:
            note = tc['note']
        custom_key = ''
        if 'custom_key' in tc:
            custom_key = tc['custom_key']
        custom_val = ''
        if 'custom_val' in tc:
            custom_val = tc['custom_val']

        note_default = ''
        if scmlabel != '1.1.1.1' and platform != 'TestProd':
            note_default = 'BuildVersion:' + scmlabel + '__Product' + platform
            if note:
                note_default = note_default + '__Note:' + note

        transform_result = {'PASSED': 'pass', 'FAILED': 'fail', 'SKIPPED': 'untested'}
        if result in transform_result:
            result = transform_result[result]

        execdata = 'EXECDATA' + '_' + custom_key

        rpc_query_string = '?rpctoken=' + self.token + '&username=' + self.user_name + '&suite=' + aptest_suite_name + '&command=result&sess=' + session_number + '&uuid=' + uuid + '&result=' + result + '&' + execdata + '=' + custom_val + '&note=' + note_default
        rpc_query_string = rpc_query_string.replace('[', '\[')
        rpc_query_string = rpc_query_string.replace(']', '\]')

        rpc_url = 'https://' + self.host + '/run/rpc.mpl' + rpc_query_string
        logger.info("DEBUG: RPC URL is: " + rpc_url)
        params = ['--connect-timeout', '20', '--silent', '-k']
        params.append(rpc_url)

        try:
            rpc_result_string = subprocess.Popen(['curl'] + params, stdout=subprocess.PIPE).communicate()[0]
            return_string = rpc_result_string.decode('ASCII')
            rpc_result_list = return_string.split('\n')

            rpc_return_value = rpc_result_list[0]
            rpc_return_message = rpc_result_list[1]

            logger.info("DEBUG: RPC result value is: " + rpc_return_value)
            logger.info("DEBUG: RPC result message is: " + rpc_return_message)

            return rpc_return_value
        except:
            logger.error("ERROR: Unable to run rpc query")
            return


# if __name__ == '__main__':
#     ap = ApTest()
#     cts_result = [{'uuid': '8A271988-0464-11DE-860E-445A00F93527', 'result': 'PASSED'},
#                   {'uuid': '8A39711E-0464-11DE-860E-445A00F93527', 'result': 'PASSED', 'note': '[trialrun]'}]
#     scmlabel = '6.5.2.2-44n'
#     platform = '5600'
#     ap.upload_aptest(cts_result, platform, scmlabel)
