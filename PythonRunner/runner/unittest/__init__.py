import argparse
import os
import re
import sys
import datetime
from runner.settings import Params, logger

def _process_args(args):
    args_str = ' '.join(args)
    args_str = args_str.replace('-var ', '').replace('G_', '--g_')
    build_match = re.search(r'(\s*--g_BUILD=[^ ]+)',args_str, re.I)
    tenant_build_match = re.search(r'(\s*--g_TENANT_BUILD=[^ ]+)',args_str, re.I)
    prebuild_match = re.search(r'(\s*--g_PREBUILD=[^ ]+)',args_str, re.I)
    scmlabel_match = re.search(r'(\s*--g_scmlabel=[^ ]+)',args_str, re.I)
    build = ''
    prebuild = ''
    tenant_build = ''
    scmlabel = ''
    if build_match:
        build = build_match.group(1)
        args_str = args_str.replace(build, '')
        build =re.sub(r'--g_BUILD','--g_build',build, re.I)
    if tenant_build_match:
        tenant_build = tenant_build_match.group(1)
        args_str = args_str.replace(tenant_build, '')
        tenant_build =re.sub(r'--g_TENANT_BUILD','--g_tenant_build',tenant_build, re.I)
    if scmlabel_match:
        scmlabel = scmlabel_match.group(1)
        args_str = args_str.replace(scmlabel, '')
        scmlabel =re.sub(r'--g_SCMLABEL','--g_scmlabel',scmlabel, re.I)
    if prebuild_match:
        prebuild = prebuild_match.group(1)
        args_str = args_str.replace(prebuild, '')
        prebuild =re.sub(r'--g_PREBUILD','--g_prebuild',prebuild, re.I)

        # args_str = args_str + scmlabel
    # else:
    args_str = args_str.lower().replace('-rv ', '--')
    args_str = args_str.replace(scmlabel, '').lower().replace('-rv ', '--') + build + tenant_build + scmlabel + prebuild
    return args_str.split(' ')

temp_args = _process_args(sys.argv[1:])
parser = argparse.ArgumentParser(description="Parse test suite arguments")
parser.add_argument('--g_cc', action="store", dest="cc", required=False)
parser.add_argument('--g_scmlabel', action="store", dest="scmlabel")
parser.add_argument('--g_testbed', action="store", dest="testbed", required=False)
parser.add_argument('--g_avt_mountpoint', action="store", dest="avt_mountpoint", required=False)
parser.add_argument('--g_build', action="store", dest="build", required=False)
parser.add_argument('--g_prebuild', action="store", dest="prebuild", required=False)
parser.add_argument('--g_tenant_build', action="store", dest="tenant_build", required=False)
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
parser.add_argument('-trialrun', action="store_true", default=False, required=False)
parser.add_argument('--no_database', action="store_true", default=False, required=False)
parser.add_argument('--g_swvertype', action='store', dest='swvertype', required=False)
parser.add_argument('-skip_dts', action="store_true", default=False, required=False)
parser.add_argument('-dev', action="store_true", default=False, required=False)
parser.add_argument('-noapi', action="store_true", default=False, required=False)
parser.add_argument('-smk', action="store_true", default=False, required=False)
###for ui test
parser.add_argument('-w', "--browser", type=str, dest='browser_type', default='firefox')
parser.add_argument('-t', "--test_type", type=str, dest='test_type', default='ui')

known, unknown = parser.parse_known_args(temp_args)
val = vars(known)
try:
    for val_unknown in unknown:
        match= re.search(r'(.*)=(.*)',val_unknown)
        setattr(Params, match.group(1), match.group(2))
except:
    pass
Params.command = sys.argv
Params.path = "//depot/SQA" + sys.argv[0]

if val['cc']: Params.cc = val['cc']
if val['scmlabel']: Params.scmlabel = val['scmlabel']
if val['testbed']: 
    Params.testbed = val['testbed'].upper()
    os.environ['G_TESTBED'] = val['testbed'].upper()
if val['avt_mountpoint']: Params.avt_mountpoint = val['avt_mountpoint']
if val['build']: Params.build = val['build']
if val['prebuild']: Params.prebuild = val['prebuild']
if val['tenant_build']: Params.tenant_build = val['tenant_build']
if val['product']: Params.product = val['product'].upper()
if val['user']: 
    Params.user = val['user']
else:
    logger.warning('Default mail to_user is specified by --g_user or suite owner. And cc_users is automation and shanghai_automation')
    logger.warning('Please specify --g_user if you want to receive mail.')
if val['requesttime']: Params.requesttime = val['requesttime']
if val['mount_point']: Params.mount_point = val['mount_point']
if val['qbs']: Params.qbs = val['qbs']
if val['resource']: Params.resource = val['resource']
if val['bundle']: Params.bundle = val['bundle']
if val['rgname']: Params.rgname = val['rgname'].upper()
if val['openstack']: 
    Params.openstack = val['openstack']
    os.environ['G_OPENSTACK'] = str(val['openstack'])
if val['setuptestbed']: Params.setuptestbed = val['setuptestbed']
if val['setupjoblog']: Params.setupjoblog = val['setupjoblog']
if val['openstack_tid']: 
    Params.openstack_tid = val['openstack_tid']
    os.environ['G_OPENSTACK_TID'] = str(val['openstack_tid'])

if val['starttime']:
    Params.starttime = datetime.datetime.strptime(val['starttime'], '%Y-%m-%d %H:%M:%S')
else:
    Params.starttime = datetime.datetime.now().replace(microsecond=0)

if val['log_level']: 
    Params.log_level = val['log_level'].upper()
    logger.setLevel(Params.log_level)
if val['log_dir']: Params.log_dir = val['log_dir']
if val['version']: Params.version = val['version']

if val['dev']:
    os.environ["SONICOS_HOME"] = '/DEV_TESTS/SonicOS'
    os.environ["PYTHON_SONICOS_HOME"] = '/DEV_TESTS/python_SonicOS'
    os.environ["PYTHON_COMMON_HOME"] = '/DEV_TESTS/python_SonicOS/common_lib'
if val['sonicos_ver']:
    Params.sonicos_ver = val['sonicos_ver']
    ver_to_remove = val['sonicos_ver'] + "/"
    Params.path = Params.path.replace(ver_to_remove, "")
    os.environ["PYTHON_SONICOS_HOME"] = os.environ["PYTHON_SONICOS_HOME"] + '/' + Params.sonicos_ver
    os.environ["SONICOS_HOME"] = os.environ["SONICOS_HOME"] + '/' + Params.sonicos_ver

if val['trialrun']: Params.trialrun = val['trialrun']
if val['no_database']: Params.no_database = val['no_database']
Params.noapi = val['noapi']
Params.smk = val['smk']

###for UI7 test
if val['browser_type']: Params.browser_type = val['browser_type']
if val['test_type']: Params.test_type = val['test_type']

Params.requesttime = Params.requesttime.replace("_", " ")

Params.ts_actual_name = sys.argv[0].replace("/SWIFT4.0/TESTS/","")
if Params.no_database or Params.trialrun:
    Params.db_upload = "No"

if Params.testbed == '':
    Params.testbed = os.uname()[1]

if Params.product == '':
    Params.product = 'testProd'

# remove "-PC1" from the testbed name
try:
    Params.testbed = re.match('(.*)-PC1', Params.testbed, re.I).group(1)
except:
    pass