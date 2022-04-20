import logging
import os
import subprocess

import config

config = config.get_config()
script_root = config["paths"]["script_root"]

logger = logging.getLogger(__name__)


def chmod_chown(drop_f):
    error = False
    start_msg = f"\n\n=========================== START PERMISSIONS FIX ==========================="
    logger.info(start_msg)
    for folder in drop_f:
        try:
            os.chdir(script_root)
            # print(f"======== PATH: {folder}  ========")
            capturedoutput = subprocess.run(
                ["sudo", "./permissions_fix.sh", folder],
                shell=False,
                capture_output=True,
                universal_newlines=True,
                check=True,
                timeout=120,
                bufsize=100,
            )
            logger.info(f"\n\\ {capturedoutput} \n\\ ")

        except Exception as e:
            perm_err_msg = f"Error on file permissions subprocess: \n {e}"
            logger.error(perm_err_msg)
            error = True

    end_msg = f"\n=========================== END PERMISSIONS FIX ===========================\n"
    logger.info(end_msg)
    return "done"


if __name__ == "__main__":
    chmod_chown()
