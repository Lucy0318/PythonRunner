import subprocess
import os
from os import environ
from xml.dom import minidom
import re
import time
import requests
import sys
from winrunner.settings import LOGGING,debug_logger
import shutil

logger = LOGGING.getLogger(__name__)


class log:
    def __init__(self, resource, product, scmlabel, testbed, user, log_ftp_server='10.203.15.20', log_path='/tmp'):
        self.log_ftp_server = log_ftp_server
        self.log_path = log_path

        self.openstack_setup = {'VTB300-PC1': '1', 'VTB400-PC1': '1', 'VTB500-PC1': '1', 'VTB501-PC1': '1', 'VTB600-PC1': '1', 'VTB700-PC1': '1', 'VTB800-PC1': '1', 'VTB900-PC1': '1'}
        self.openstack = ''
        if environ.get('G_OPENSTACK') is not None:
            self.openstack = os.environ['G_OPENSTACK']
            debug_logger.debug("self.openstack :" + str(self.openstack))

        self.resource = resource
        self.product = product
        self.scmlabel = scmlabel
        self.testbed = testbed
        self.user = user
        self.consoles = []
        self.logfile = {}
        self.index = {}

        debug_logger.debug(" resource  :" + str(self.resource))
        debug_logger.debug(" product  :" + str(self.product))
        debug_logger.debug(" scmlabel  :" + str(self.scmlabel))
        debug_logger.debug(" user :" + str(self.user))
        # uploaddir = '/logs/buildtestlogs/' + self.product + '/' + self.scmlabel + '/' + self.testbed + '/' + self.user + '/'
        # uploaddir = 'X:/logs/buildtestlogs/' + self.testbed + '/'
        debug_logger.debug("*** mkdir log file ***")
        uploaddir = 'X:/logs/buildtestlogs/' + self.product + '/' + self.scmlabel + '/' + self.testbed + '/' + self.user + '/'
        self.uploaddir = uploaddir
        debug_logger.debug("*** uploaddir1 ***" + str(self.uploaddir))

    def copy_file_to_log_server(self, file_name):
        mount_log_ip = ""
        debug_logger.info("*** COPY FILE TO LOG SERVER BEGIN ***")
        debug_logger.info("*** file_name *** :" + str(file_name))
        timenow = time.strftime("%S", time.gmtime())

        uploaddir = self.uploaddir + self.user + '_' + self.testbed + '_' + timenow + '/'
        # uploaddir = self.uploaddir + self.testbed + '_' + timenow
        debug_logger.info("SELF USER : " + str(self.user))
        debug_logger.debug("*** uploaddir ***" + str(uploaddir))
        dst = uploaddir
        src = file_name

        params = ['-avz']
        params.extend((src, dst))
        debug_logger.debug("PARAMS : " + str(params))
        debug_logger.debug("DST : " + str(dst))

        try:
            debug_logger.info(" ***In try catch ***")
            if not os.path.exists(dst):
                os.makedirs(dst)
            debug_logger.info("*** File created ***")
            debug_logger.debug("params  : " + str(params))
            source = params[1].replace('/', '\\')
            dest = params[2]
            debug_logger.debug(" source " + str(source))
            debug_logger.debug(" destination " + str(dest))
            source_filename = source.split('\\')
            debug_logger.debug("source filename : " + str(source_filename[4]))
            debug_logger.debug("final filename : " + str(dest) + '/' + str(source_filename[4]))
            # print("source permission : ", os.stat(source))
            # print("dest permission : ", os.stat(dest))
            # f1 = open(dest+"trial.txt", "w+")
            # f1 = open(dest+"/trial.txt", "w+")
            f1 = open(dest + '/' + source_filename[4], "w+")
            f = open(source)
            # f.close()
            # print("File written")
            debug_logger.debug(" dest  " + str(dest))
            # rsync_result_string = subprocess.Popen(['rsync'] + params, stdout=subprocess.PIPE).communicate()[0]
            # rsync_result_string = shutil.copyfile(source, dest)
            for line in f:
                f1.write(line)
            f.close()
            f1.close()
            # print("RSYNC RESULT STRING : ", rsync_result_string)

            mtab_cmd = []
            op_system = sys.platform
            debug_logger.debug("OP_SYSTEM : " + str(op_system))
            if op_system == 'linux':
                mtab_cmd = ['cat', '/etc/mtab']
            else:
                mtab_cmd = ['/cygdrive/c/WINDOWS/system32/net', 'use']

            #mtab_params = ['/etc/mtab']
            # mtab_result_string = subprocess.Popen(mtab_cmd, stdout=subprocess.PIPE).communicate()[0]
            # mtab_result_string = mtab_result_string.decode('ASCII')

            # result = re.search(r'\b(\d+\.\d+\.\d+\.\d+)(\:/|\\)logs\b', mtab_result_string)
            # ip = result.group(1)
            # ip = "10.5.64.10:/logs"
            mount_ip_list = subprocess.Popen(["wmic", "logicaldisk", "get", "providername"], stdout=subprocess.PIPE)
            mount_ip_list = str(mount_ip_list.communicate()[0]).replace(" ", "").replace(r'\\', '')
            mount_ip_list = mount_ip_list.replace(r'\r', '').split(r'\n')
            debug_logger.debug("*** IP MOUNT : *** " + str(mount_ip_list))
            for i in mount_ip_list:
                if i.find('logs') != -1:
                    debug_logger.debug(" required mount :  " + str(i[:-4]))
                    mount_log_ip = i[:-4]
            # ip = "10.5.64.10"
            ip = mount_log_ip
            debug_logger.debug("To be replaced : " + str(uploaddir))
            # uploaddir = uploaddir.replace('/logs', '')
            uploaddir = 'http://' + ip + uploaddir
            uploaddir = uploaddir.replace('X:', '')
            debug_logger.debug("final uploaddir  : " + str(uploaddir))
        except Exception as e:
            debug_logger.debug("EXCEPTION : " + str(e))
            logger.error("Unable to rsync files or /logs nfs mount cannot be determined from /etc/mtab")
            debug_logger.error("Unable to rsync files or /logs nfs mount cannot be determined from /etc/mtab")
            return 1
        debug_logger.info("*** COPY FILE TO LOG SERVER END ***")
        return uploaddir

    def get_dut_console_log_link(self):
        self.populate_console()
        console_links = []
        for tbcslname in self.consoles:
            console_link = 'http://' + self.log_ftp_server + '/console/' + tbcslname
            console_links.append(console_link)

        return console_links


    def set_console_index(self, link):
        result = re.search(r'\/([\w-]+)$', link)
        console = result.group(1)

        try:
            response = requests.get(link)
            content = response.content.decode('ASCII')
            logfile = content.split('\n')

            self.logfile[console] = logfile
            self.index[console] = len(logfile)
        except:
            logger.error("ERROR: Unable to retrieve console logfile")
            debug_logger.error("ERROR: Unable to retrieve console logfile")
            return 1

        return self


    def create_dut_console_textfile(self, file_name):
        result = re.search(r'\/([\w-]+)\.\w+$', file_name)
        console = result.group(1)

        link = self.console_links[console]

        try:
            response = requests.get(link)
            content = response.content.decode('ASCII')
            logfile = content.split('\n')

            current_content = logfile[self.index[console]:]

            with open(file_name, "w", newline="") as file_handle:
                file_handle.writelines(current_content)
                file_handle.close()
        except:
            logger.error("Unable to write console textfile")
            debug_logger.error("Unable to write console textfile")
            return 1

        return 0

    def populate_console(self):
        testbed = self.testbed
        product = self.product
        product = re.sub(r'pro|nsa|octeon', '', product.lower())

        tbdefcsl = ''
        if self.openstack != '1':
            tbdefcsl = testbed.lower() + '-' + product

            tqtest_resource = self.resource
            tqtest_resources = tqtest_resource.split(',')
            for element in tqtest_resources:
                element = re.sub(r':\d+$', '', element)
                logger.info("RESOURCE ELEMENT: " + element)
                debug_logger.info("RESOURCE ELEMENT: " + element)

                if re.match(r'^(SHA|CLUSTER)$', element):
                    console = tbdefcsl
                    tbdefcsl = console + '-pri'
                    self.consoles.append(tbdefcsl)
                    tbdefcsl = console + '-sec'
        elif not self.testbed in self.openstack_setup:
            try:
                xml = self.testbed + '.xml'
                xml_path = 'http://osservices-sj.eng.sonicwall.com/topologies/' + xml

                content = self.log_path + '/' + xml
                cmd = ['/bin/rm', '-Rf', content]
                retval = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

                params = ['-P', self.log_path, xml_path]
                retval = subprocess.Popen(['wget'] + params, stdout=subprocess.PIPE).communicate()[0]

                doc = minidom.parse(content)
                rec = doc.getElementsByTagNameNS('*', 'topology')[0]
                console = rec.getElementsByTagName('node')[0]
                tbdefcsl = console.getElementsByTagName('topology-resource-name')[0].firstChild.data
            except:
                logger.error("Unable to retrieve xml file from osservices")
                debug_logger.error("Unable to retrieve xml file from osservices")
                return 1

        self.consoles.append(tbdefcsl)

        return self


# if __name__ == "__main__":
#     python_object = log()
#
#     file_name = '/home/gavin/Python_Runner_Logs/eu_test_suite.log'
#     url = python_object.copy_file_to_log_server(file_name)
#
#     print(url)
#
#     links = python_object.get_dut_console_log_link()
#     print(links)
#     for console_log in links:
#         python_object.set_console_index(console_log)
#
#     for console in python_object.consoles:
#         filename = '/home/gavin/Python_Runner_Logs/' + console + '.txt'
#         python_object.create_dut_console_textfile(filename)


# export PYTHONPATH
# export G_SCMLABEL=6.5.2.2-44n
# export G_PRODUCT=5600
# export G_TESTBED=TB24
# export G_USER=root
# export G_RESOURCE=CLUSTER:1
