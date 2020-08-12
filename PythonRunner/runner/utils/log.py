import subprocess
import os
from os import environ
from xml.dom import minidom
import re
import time
import requests
import sys
from runner.settings import logger, python_logger, LOG_DIR, TIMENOW


class log:
    def __init__(self, resource, product, scmlabel, testbed, user, log_ftp_server='10.203.15.20', log_path='/tmp'):
        self.log_ftp_server = log_ftp_server
        self.log_path = log_path

        self.openstack_setup = {'VTB300-PC1': '1', 'VTB400-PC1': '1', 'VTB500-PC1': '1', 'VTB501-PC1': '1', 'VTB600-PC1': '1', 'VTB700-PC1': '1', 'VTB800-PC1': '1', 'VTB900-PC1': '1'}
        self.openstack = ''
        if environ.get('G_OPENSTACK') is not None:
            self.openstack = os.environ['G_OPENSTACK']

        self.resource = resource
        self.product = product
        self.scmlabel = scmlabel
        self.testbed = testbed
        self.user = user
        self.consoles = []
        self.logfile = {}
        self.index = {}
        op_system = sys.platform
        if op_system == 'linux':
            mtab_cmd = ['cat', '/etc/mtab']
        else:
            mtab_cmd = ['/cygdrive/c/WINDOWS/system32/net', 'use']
        mtab_result_string = subprocess.Popen(mtab_cmd, stdout=subprocess.PIPE).communicate()[0]
        mtab_result_string = mtab_result_string.decode('ASCII')

        result = re.search(r'\b(\d+\.\d+\.\d+\.\d+)(\:/|\\)logs\b', mtab_result_string)
        ip = result.group(1)
        self.uploaddir = '/logs/buildtestlogs/' + self.product + '/' + self.scmlabel + '/' + self.testbed + '/' + self.user + '/'+ self.user + '_' + self.testbed + '_' + TIMENOW + '/'
        self.uploaddir_url = self.uploaddir.replace('/logs', '')
        self.uploaddir_url = 'http://' + ip + self.uploaddir_url + os.path.basename(LOG_DIR) + '/'

    def copy_file_to_log_server(self, file_name):
        uploaddir = self.uploaddir
        dst = uploaddir
        src = file_name

        params = ['-avz']
        params.extend((src, dst))
        python_logger.write('Entering utils::log::copy_file_to_log_server...'+ '\n' )
        python_logger.write(''*4 + 'Rsyncing logs rsync: '+ ' '.join(['rsync'] + params)+ '\n')

        try:
            if not os.path.exists(dst):
                os.makedirs(dst)
            rsync_result_string = subprocess.Popen(['rsync'] + params, stdout=subprocess.PIPE).communicate()[0]

            #mtab_params = ['/etc/mtab']
            python_logger.flush()
        except:
            logger.error("Unable to rsync files or /logs nfs mount cannot be determined from /etc/mtab")
            return 1
        return uploaddir

    def get_dut_console_log_link(self):
        self.populate_console()
        console_links = []
        try:
            for tbcslname in self.consoles:
                console_link = 'http://' + self.log_ftp_server + '/console/' + tbcslname
                console_links.append(console_link.lower())
        except:
            logger.warning('Unable to get dut console log link.')

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
