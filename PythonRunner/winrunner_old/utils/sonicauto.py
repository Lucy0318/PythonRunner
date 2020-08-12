from winrunner.utils.models import User, Platform, TestSuite, TestBed, JobRequest, TestResult, ApTestSessionGroup
from winrunner.settings import Params, get_sonicauto_session, LOGGING, debug_logger

logger = LOGGING.getLogger(__name__)


class SonicAuto:
    default_args = {
        'g_cc': '',
        'g_scmlabel': '',
        'g_testbed': '',
        'g_avt_mountpoint': '',
        'g_build': '',
        'g_product': '',
        'g_user': '',
        'g_requesttime': '',
        'mount_point': '',
        'g_qbs': '',
        'g_resource': '',
        'bundle': '',
        'rgname': '',
        'log_level': '',
        'log_dir': ''
    }

    def __init__(self):
        debug_logger.info("*** init ***")
        self.session = get_sonicauto_session()

    def get_session_group_name(self, scmlabel, productid):
        try:
            session_group = self.session.query(ApTestSessionGroup).filter(ApTestSessionGroup.scmlabel == scmlabel).filter(ApTestSessionGroup.productid == productid)
            debug_logger.debug("session_group[0].group_name :" + str(session_group[0].group_name))
            return session_group[0].group_name
        except Exception as e:
            logger.error(f"Not able to get session group name for scmlabel {scmlabel} and productid {productid}")
            debug_logger.error(f"Not able to get session group name for scmlabel {scmlabel} and productid {productid}")
            return ''

    def get_product_id_from_platform(self, platform):
        try:
            data = self.session.query(Platform).filter(Platform.alias == platform)
            debug_logger.debug("data[0].productid" + str(data[0].productid))
            return data[0].productid
        except Exception as e:
            logger.error(f"Not able to get product id from platform {platform}")
            debug_logger.error(f"Not able to get product id from platform {platform}")
            return 0

    def get_testsuite_details(self, pathname):
        try:
            debug_logger.info("*** session.query ***")
            debug_logger.debug("*** pathname_old *** :" + str(pathname))
            # pathname_new = pathname.replace('\\', '/').replace('Y:', '/')
            # pathname_new = "//depot/SQA/SWIFT4.0/TESTS/Application/MSW/MSW_API_Automation/RESTAPI-1/Selenium/test_suite/MSW_Sanity_WCM_Suite_ts.py"
            # pathname_new = r'Z:\SWIFT4.0\TESTS\Application\MSW\MSW_API_Automation\RESTAPI-1\Selenium\test_suite\MSW_Sanity_WCM_Suite_ts.py'
            # debug_logger.debug("*** pathname_new *** :" + str(pathname_new))
            suites = self.session.query(TestSuite).filter(TestSuite.path == pathname)
            # debug_logger.debug("***NEWPATHNAME*** : " + str(pathname_new))
            debug_logger.debug("***TESTSUITE*** : " + str(TestSuite))
            debug_logger.debug("***TESTSUITE.PATH*** : " + str(TestSuite.path))
            debug_logger.debug("***PATHNAME*** : " + str(pathname))
            debug_logger.debug("***SUITES*** : " + str(suites))
            '''debug_logger.debug("***SUITES[0]*** : " + str(suites[0]))
            debug_logger.debug("***SUITES[0].TESTCASES*** : " + str(suites[0].testcases))
            debug_logger.debug("***SUITES[0].EXECTIME*** : " + str(suites[0].exectime))
            debug_logger.debug("***SUITES[0].DISPLAYNAME*** : " + str(suites[0].display_name))'''
            debug_logger.debug("Getting test data")
            '''if len(str(suites)) == 0:
                debug_logger.debug("Length of the suites is 0 ")'''
            data = {
                'testcases': suites[0].testcases,
                'exectime': suites[0].exectime,
                'display_name': suites[0].display_name
            }
        except Exception as e:
            logger.error(f"Not able to get test suite details for {pathname}")
            debug_logger.error(f"Not able to get test suite details for {pathname}")
            data = {
                'testcases': 'No record',
                'exectime': 'No record',
                'display_name': pathname.split('/')[-1]
            }
        debug_logger.debug("*** DATA *** :" + str(data))
        return data

    def get_testsuite_owner(self, pathname):
        try:
            suites = self.session.query(TestSuite).filter(TestSuite.path == pathname)
            users = self.session.query(User).filter(User.userid == suites[0].ownerid)
            data = {
                'name': users[0].name
            }
            return data
        except Exception as e:
            logger.error(f"Not able to get test suite owner for {pathname}")
            debug_logger.error(f"Not able to get test suite owner for {pathname}")
            return ''

    def get_full_name(self, username):
        try:
            users = self.session.query(User).filter(User.name == username)
            data = {
                'full_name': users[0].full_name
            }
            return data
        except Exception as e:
            logger.error(f"Not able to get full name for username {username}")
            debug_logger.error(f"Not able to get full name for username {username}")
            return ''

    def get_backup_owner(self, pathname):
        try:
            suites = self.session.query(TestSuite).filter(TestSuite.path == pathname)
            users = self.session.query(User).filter(User.userid == suites[0].backup_ownerid)
            data = {
                'name': users[0].name
            }
            return data
        except Exception as e:
            logger.error(f"Not able to get backup owner for {pathname}")
            debug_logger.error(f"Not able to get backup owner for {pathname}")
            return ''

    def save_job_request(self):
        try:
            # Get userid
            users = self.session.query(User).filter(User.name == Params.user)
            debug_logger.debug("User value : " + str(User))
            debug_logger.debug("Params.user : " + str(Params.user))
            debug_logger.debug("users query result : " + str(users))

            # Get suiteid
            suites = self.session.query(TestSuite).filter(TestSuite.path == Params.path)
            debug_logger.debug("Test Suite value : " + str(TestSuite))
            debug_logger.debug("Params.path : " + str(Params.path))
            debug_logger.debug("suites query result : " + str(suites))

            # Get tbid
            testbeds = self.session.query(TestBed).filter(TestBed.name == Params.testbed)
            debug_logger.debug("testbeds value : " + str(testbeds))
            debug_logger.debug("Params.testbed : " + str(Params.testbed))
            debug_logger.debug("testbeds query result : " + str(testbeds))

            # Get platformid
            platforms = self.session.query(Platform).filter(Platform.alias == Params.product)
            debug_logger.debug("Platform value : " + str(Platform))
            debug_logger.debug("Params.product : " + str(Params.product))
            debug_logger.debug("platforms query result : " + str(platforms))

            # topology_id: not added at this moment
            job_request = JobRequest()
            debug_logger.debug(" *** users, suites, testbeds, platforms *** :" + str(users)
                               + str(suites) + str(testbeds) + str(platforms))
            debug_logger.debug(" *** job_request *** :" + str(job_request))
            job_request.qbsjobid = Params.qbsjobid
            debug_logger.debug("Job_request_id :" + str(job_request.qbsjobid))
            job_request.jobname = Params.bundle
            debug_logger.debug("Job_request_jobname :" + str(job_request.jobname))
            job_request.qbs_serverid = Params.qbs
            debug_logger.debug("Job_request_serverid :" + str(job_request.qbs_serverid))
            job_request.requested_by = users[0].userid
            debug_logger.debug("Job_request_requested_by :" + str(job_request.requested_by))

            try:
                debug_logger.debug("Job_request_suiteid- suites :" + str(suites))
                debug_logger.debug("suites[0] : " + str(suites[0]))
                job_request.suiteid = suites[0].testsuiteid
            except Exception as se:
                debug_logger.debug("Exception for suite : " + str(se))
                job_request.suiteid = None

            debug_logger.debug("Job_request_suiteid :" + str(job_request.suiteid))
            # job_request.command = Params.command

            # This is being done because to save the test suite, you need path in a different format
            job_request_temp = str(Params.command).replace('\\', '/').replace('Z:', '/SWIFT4.0').replace('//', '/')
            job_request.command = job_request_temp

            debug_logger.debug("Original _job_request_command :" + str(Params.command))
            debug_logger.debug("Changed_(for sonicauto saving)_Job_request_temp : " + str(job_request.command))
            job_request.platformid = platforms[0].platformid
            debug_logger.debug("Job_request_platformid : " + str(job_request.platformid))
            job_request.tbid = testbeds[0].tbid
            debug_logger.debug("Job_request_tbid :" + str(job_request.tbid))
            job_request.scmlabel = Params.scmlabel
            debug_logger.debug("Job_request_scmlabel :" + str(job_request.scmlabel))
            job_request.log_location = Params.log_location
            debug_logger.debug("Job_request_log_location :" + str(job_request.log_location))
            job_request.requested_time = Params.requesttime
            debug_logger.debug("Job_request_requestedtime :" + str(job_request.requested_time))
            job_request.start_time = Params.starttime
            debug_logger.debug("Job_request_start_time :" + str(job_request.start_time))
            job_request.build_file = Params.build
            debug_logger.debug("Job_request_build_file :" + str(job_request.build_file))

            print("********* job_request *************** :", job_request)

            self.session.add(job_request)
            self.session.commit()
            self.session.refresh(job_request)

            return job_request.job_requestid
        except Exception as e:
            print("********* job_request *************** :", job_request)
            logger.error(f"Not able to save job request with error {e.args}")
            debug_logger.error(f"Not able to save job request with error {e.args}")
            return ''

    def save_result(self, results: list):
        debug_logger.debug("*** save_result ***")
        job_requestid = self.save_job_request()

        if job_requestid == '':
            return 'Error: not able to create job_request record into database'
        else:
            i=0
            while i < len(results):
                tc = dict(results[i])
                tc['job_requestid'] = job_requestid
                self.save_test_case_result(res=tc)
                i += 1

        return 'Result got saved successfully'

    def save_test_case_result(self, res={}):
        try:
            test_result = TestResult()
            test_result.matrixid = res['matrixid']
            debug_logger.debug("test_result.matrixid :" + str(test_result.matrixid))
            test_result.job_requestid = res['job_requestid']
            test_result.type = res['type']
            test_result.title = res['title']
            test_result.parameters = res['parameters']
            debug_logger.debug("test_result.parameters :" + str(test_result.parameters))
            test_result.alias = res['alias']
            debug_logger.debug("test_result.alias :" + str(test_result.alias))
            test_result.result = res['result']
            debug_logger.debug("test_result.result :" + str(test_result.result))
            test_result.starttime = res['starttime']
            test_result.endtime = res['endtime']
            test_result.filename = res['filename']
            debug_logger.debug("test_result.filename :" + str(test_result.filename))
            test_result.log_link = res['log_link']
            debug_logger.debug("test_result.log_link :" + str(test_result.log_link))
            test_result.uuid = res['uuid']

            self.session.add(test_result)
            self.session.commit()
            self.session.refresh(test_result)
            print("************ test_result ************* :", test_result)
            debug_logger.debug("test_result :" + str(test_result))
            return test_result.resultid
        except Exception as e:
            logger.error(f"Not able to save test case result with error {e.args}")
            debug_logger.error(f"Not able to save test case result with error {e.args}")
            return ''

# if __name__ == '__main__':
#
#      sa = SonicAuto()
#      id = sa.get_product_id_from_platform('5600')
#      print(sa.get_session_group_name('6.2.7.1-21n', id))
#      sa.exit()
#
#     command = "python3 /tmp/unittest/eu_test_suite.py"
#     log_location = "/Results/logs"
#
#     sa.args['qbsjobid'] = '9016408'
#     sa.args['command'] = command
#     sa.args['log_location'] = log_location
#     sa.args['g_cc'] = 'snataraj'
#     sa.args['g_testbed'] = 'VTB522'
#     sa.args['g_avt_mountpoint'] = 'null'
#     sa.args['g_build'] = '/logs/downloads/snataraj-1550940730068_fake_fw.sig'
#     sa.args['g_product'] = '5600'
#     sa.args['g_scmlabel'] = 'cc_weekly_ui_rerun[23-02-2019]'
#     sa.args['g_user'] = 'snataraj'
#     sa.args['g_requesttime'] = '2019-02-23 08:59:58'
#     sa.args['g_qbs'] = '1'
#     sa.args['bundle'] = 'snataraj-1550940730068'
#     sa.args['path'] = '//depot/SQA/SWIFT4.0/TESTS/SonicOS/SST/GAV_Evasion/testsuites/gav_evasion.cts'
#     sa.args['starttime'] = '2019-02-24 09:00:00'
#
#     job_requestid = sa.save_job_request()
#
#     tc_result = {
#         'matrixid': '',
#         'job_requestid': job_requestid,
#         'type': 'TestCase',
#         'title': 'This is a test for PythonRunner',
#         'parameters': '--g_cc=test',
#         'alias': '',
#         'result': 'PASSED',
#         'starttime': '',
#         'endtime': '',
#         'filename': 'unittest.py',
#         'log_link': '/tmp/pythonrunner/logs.txt',
#         'uuid': '1234-2345-4567-7890'
#     }
#
#     sa.save_test_case_result(tc_result)
#
#     sa.exit()
