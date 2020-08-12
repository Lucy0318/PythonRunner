import sys
import os
import paramunittest

from runner.unittest.setup import Test
from runner.utils.assertion import Assertion
from runner.settings import logger
sys.path.append('/DEV_TESTS/python_SonicOS/6.5.4')
sys.path.append('/DEV_TESTS/python_SonicOS/common_lib')
from utm import Firewall
from lib.modules.CLI import network

fw = Firewall('192.168.168.168', user='admin', password='password', supported_config_mode='cli-ssh')
interface_instance = network.InterfaceCli(fw)

@paramunittest.parametrized(
    {"interface": 'X1', 'ip': '1.1.1.1', 'zone': 'WAN', 'uuid': '111111'},
    {"interface": 'X2', 'ip': '2.2.2.2', 'zone': 'WAN', 'uuid': '222222'},
)


class TestConfigInterface(Test):
    def setParameters(self, interface, ip, zone, uuid):
        '''parameter if,ip,zone,uuid must be same with the dict above'''
        self.interface = interface
        self.ip = ip
        self.zone = zone
        self.uuid = uuid
        
    def test_00_01_Config(self):
        interface_dict = {
            'if': self.interface,
            'zone': self.zone, 
            'mode': 'static',
            'ip': self.ip,
            'netmask': '255.255.255.0',
        }
        rc = interface_instance.config_interface(**interface_dict)
        Assertion.assert_equal(rc, True, "ERR: Config {} to static failed".format(self.interface))


