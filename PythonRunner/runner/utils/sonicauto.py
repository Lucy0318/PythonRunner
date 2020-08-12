import re
from runner.utils.models import User, Platform, TestSuite, TestBed, JobRequest, TestResult, ApTestSessionGroup, TestFailure, FailureType
from runner.settings import Params, get_sonicauto_session, LOGGING

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
        self.session = get_sonicauto_session()

    def get_session_group_name(self, scmlabel, productid):
        try:
            session_group = self.session.query(ApTestSessionGroup).filter(ApTestSessionGroup.scmlabel == scmlabel).filter(ApTestSessionGroup.productid == productid)
            return session_group[0].group_name
        except Exception as e:
            logger.error(f"Not able to get session group name for scmlabel {scmlabel} and productid {productid}")
            return ''

    def get_product_id_from_platform(self, platform):
        try:
            data = self.session.query(Platform).filter(Platform.alias == platform)
            return data[0].productid
        except Exception as e:
            logger.error(f"Not able to get product id from platform {platform}")
            return 0

    def get_testsuite_details(self, pathname):
        try:
            suites = self.session.query(TestSuite).filter(TestSuite.path == pathname)
            data = {
                'testcases': suites[0].testcases,
                'exectime': suites[0].exectime,
                'display_name': suites[0].display_name
            }
        except Exception as e:
            logger.error(f"Not able to get test suite details for {pathname}: {e}")
            data = {
                'testcases': 'No record',
                'exectime': 'No record',
                'display_name': pathname.replace('//depot/SQA','').split('/')[-1][:-3],
            }

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
            return ''

    def get_full_name(self, username):
        try:
            users = self.session.query(User).filter(User.name == username)
            data = {
                'full_name': users[0].full_name
            }
            return data
        except Exception as e:
            logger.error("Not able to get full name for username {username}")
            data = {
                'full_name': 'root'
            }
            return data 

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
            return ''

    def save_job_request(self):
        try:
            # Get userid
            users = self.session.query(User).filter(User.name == Params.user)

            # Get suiteid
            suites = self.session.query(TestSuite).filter(TestSuite.path == Params.path)

            # Get tbid
            testbeds = self.session.query(TestBed).filter(TestBed.name == Params.testbed)

            # Get platformid
            platforms = self.session.query(Platform).filter(Platform.alias == Params.product)

            # topology_id: not added at this moment7
            job_request = JobRequest()
            try:
                job_request.topology_id = os.environ['G_OPENSTACK_TID']
            except:
                pass
            job_request.qbsjobid = Params.qbsjobid
            job_request.jobname = Params.bundle
            job_request.qbs_serverid = Params.qbs
            job_request.requested_by = users[0].userid

            try:
                job_request.suiteid = suites[0].testsuiteid
            except Exception as se:
                job_request.suiteid = None

            job_request.command = 'python3 ' + ' '.join(Params.command)
            job_request.platformid = platforms[0].platformid
            job_request.tbid = testbeds[0].tbid
            job_request.scmlabel = Params.scmlabel
            job_request.log_location = Params.log_location
            job_request.requested_time = Params.requesttime
            job_request.start_time = Params.starttime
            job_request.build_file = Params.build

            self.session.add(job_request)
            self.session.commit()
            self.session.refresh(job_request)

            return job_request.job_requestid
        except Exception as e:
            logger.error(f"Not able to save job request with error {e.args}")
            return ''

    def save_result(self, results: list):
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
            test_result.job_requestid = res['job_requestid']
            test_result.type = res['type']
            test_result.title = res['title']
            test_result.parameters = res['parameters']
            test_result.alias = res['alias']
            test_result.result = res['result']
            test_result.starttime = res['starttime']
            test_result.endtime = res['endtime']
            test_result.filename = res['filename']
            test_result.log_link = res['log_link']
            test_result.uuid = res['uuid']

            self.session.add(test_result)
            self.session.commit()
            self.session.refresh(test_result)
            if test_result.result == 'FAILED':
                try:
                    users = self.session.query(User).filter(User.name == Params.user)
                    ftype = self.session.query(FailureType).filter(FailureType.name == res['ftype'])
                    test_faiure = TestFailure()
                    test_faiure.ftypeid = ftype[0].ftypeid
                    test_faiure.freason = res['ftype']
                    test_faiure.ownerid = users[0].userid
                    test_faiure.dtsid = None
                    test_faiure.jira = None
                    test_faiure.resultid = test_result.resultid
                    if res['dts_jira_link']:
                        dts = re.search('jobid=(\d+)', res['dts_jira_link'])
                        jira = re.search(r'track.eng.sonicwall.com/browse/(.+)', res['dts_jira_link'])
                        if dts:
                            test_faiure.dtsid = int(dts.group(1))
                        elif jira:
                            test_faiure.jira = jira.group(1)
                    self.session.add(test_faiure)
                    self.session.commit()
                    self.session.refresh(test_faiure)
                    return test_faiure.failureid
                except Exception as e:
                    logger.error(f"Not able to save test failure with error {e.args}")
                    return ''
            return test_result.resultid
        except Exception as e:
            logger.error(f"Not able to save test case result with error {e.args}")
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
