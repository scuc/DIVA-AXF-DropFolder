import logging
import os
import subprocess

import config

config = config.get_config()
script_root = config["paths"]["script_root"]

logger = logging.getLogger(__name__)


def chmod_chown(drop_f):
    """
    Fix file permissions for the specified folders.

    Args:
        drop_f (list): A list of folders to fix permissions for.

    Returns:
        str: A string indicating the completion status of the function.

    Raises:
        Exception: If there is an error in the file permissions subprocess.

    """
    error = False
    start_msg = f"\n\n=========================== START PERMISSIONS FIX ==========================="
    logger.info(start_msg)
    for folder in drop_f:
        try:
            if "Isilon2" in folder.split("/") or "ng-editorial" in folder.split("/"):
                continue
            else:
                os.chdir(script_root)
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

    end_msg = "\n=========================== END PERMISSIONS FIX ===========================\n"
    logger.info(end_msg)
    return "done"


if __name__ == "__main__":
    chmod_chown()
