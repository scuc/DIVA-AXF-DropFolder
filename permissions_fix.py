
import logging
import os
import subprocess

import config

config = config.get_config()
script_root = config['paths']['script_root']

logger = logging.getLogger(__name__)


def chmod_chown():
    # subprocess.run(['sh', 'permission_fix.sh'])
    os.chdir(script_root)
    start_msg = f"\n============= START PERMISSIONS FIX =============\n"
    logger.info(start_msg)
    session = subprocess.Popen(['./permissions_fix.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = session.communicate()
    logger.info(f"\n\\ {stdout} \n\\ ")
    logger.error(f"\n\\ {stderr} \n\\ ")
    end_msg = f"\n============= END PERMISSIONS FIX =============\n"
    logger.info(end_msg)

    return


if __name__ == '__main__':
    chmod_chown()
