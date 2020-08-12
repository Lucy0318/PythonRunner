import sys
import os

from runner.unittest.setup import Test
from runner.utils.assertion import Assertion
from nose_parameterized import parameterized
from runner.settings import LOGGING, SUITE_RES_FILE_WITH_PATH
sys.path.append('/DEV_TESTS/python_SonicOS/6.5.4')
sys.path.append('/DEV_TESTS/python_SonicOS/common_lib')
from utm import Firewall
from lib.modules.CLI import network

logger = LOGGING.getLogger(__name__)
fw = Firewall('192.168.168.168', user='admin', password='password', supported_config_mode='cli-ssh')
interface_instance = network.InterfaceCli(fw)

class TestConfigInterface(Test):
    uuid = 'NonTC'
    description = 'config interface'
    @parameterized.expand([
        ("X1", 'WAN', '1.1.1.1', '255.255.255.0', '1.1.1.2'),
        ("X2", 'WAN', '2.2.2.2', '255.255.255.0', '2.2.2.3'),
    ])

    def test_00_01_Config(self, interface, mode, ip, netmask, gateway):
        interface_dict = {
            'if': interface,
            'zone': mode, 
            'mode': 'static',
            'ip': ip,
            'netmask': netmask,
            'gateway': gateway,
        }
        rc = interface_instance.config_interface(**interface_dict)
        Assertion.assert_equal(rc, True, "ERR: Config {} to static failed".format(interface))

    @parameterized.expand([
        ("X3", 'dhcp'),
        ("X4", 'dhcp'),
    ])
    def test_00_02_Config_dhcp(self, interface, mode):
        x4_dict = {
            'if': interface,
            'zone': 'WAN', 
            'mode': mode,
        }
        rc = interface_instance.config_interface(**x4_dict)
        Assertion.assert_equal(rc, True, "ERR: Config x4 to static failed")     
