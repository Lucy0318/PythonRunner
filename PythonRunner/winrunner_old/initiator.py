__author__ = 'vnaik'

import sys
import os
sys.path.append(r"/SWIFT4.0/PythonRunner")
from winrunner.settings import debug_logger


class CommandRunner(object):

    def get_command(self, args, qbs_jobnum):

        # Get testbed name on linux machine
        tbname = (os.uname()[1]).split('-')[0]

        # Verify the testbed name, qbsjobid and args has been imported properly
        debug_logger.debug("Testbed name : " + str(tbname))
        debug_logger.debug("argument 1 - args sent to get_command function : " + str(args))
        debug_logger.debug("argument 2 - qbs_jobnum sent to get_command function : " + str(qbs_jobnum))
        debug_logger.debug("argument_length : " + str(args.__len__()))

        # Edit the args to remove unwanted elements
        i = 1
        while i < args.__len__():
            if str(args[i]).find(',')  != -1:
                args[i] = args[i][:-1]
            i += 1

        # Confirm if it is DEV_TESTS or SWIFT4.0 and change path accordingly to send in windows
        if str(args[1]).find('/DEV_TESTS') != -1:
            debug_logger.debug("--- DEV TEST present --")
            path = args[1].replace('/DEV_TESTS', 'Y:').replace('/', '\\').replace('[', '').replace(',', '')
            path = path.strip()
            args[1] = path
            debug_logger.debug("--- args[1] after editing the path --- : " + str(args[1]))
        else:
            debug_logger.debug("--- SWIFT4.0 present --")
            path = args[1].replace('/SWIFT4.0', 'Z:').replace('/', '\\').replace('[', '').replace(',', '')
            path = path.strip()
            debug_logger.debug("-- path after replacing -- :" + str(path))
            args[1] = path
            debug_logger.debug("-- args[1] after editing the path -- :" + str(args[1]))

        args_str = ' '.join(args[1:])
        cmd = args_str.replace(']', '').replace('[', '')
        debug_logger.debug("command generated : " + str(cmd))
        cmd = r"python3 " + cmd + " --g_testbed " + tbname + " --g_qbs_jobnum " + str(qbs_jobnum)
        debug_logger.debug("python command generated :" + str(cmd))
        run_cmd = r'curl -G -v "http://192.168.10.20:3000" --data-urlencode "cmd=' + cmd + '"'
        debug_logger.debug("*** Final run_cmd *** : " + str(run_cmd))
        response = os.system(run_cmd)
        debug_logger.debug("response : " + str(response))

if __name__ == '__main__':
    obj = CommandRunner()
    debug_logger.debug("-- sys.argv received by initiator--- " + str(sys.argv))
    # Send only the qbs jobnum as argument 2, and everything else except qbsjobnum as argument 1
    obj.get_command(sys.argv[:-1], sys.argv[-1])
