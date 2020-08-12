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
    def test_00_01_Config(self):
#        print(self.kwargs)
        interface_dict = {
            'if': self.param['if'],
            'zone': 'WAN', 
            'mode': 'dhcp',
        }
        rc = interface_instance.config_interface(**interface_dict)
        Assertion.assert_equal(rc, True, "ERR: Config {} to static failed".format(self.param['if']))


