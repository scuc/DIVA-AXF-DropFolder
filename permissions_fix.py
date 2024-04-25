import logging
import os
import subprocess

import config

config = config.get_config()
script_root = config["paths"]["script_root"]

logger = logging.getLogger(__name__)


def fix_permissions(folders):
    """
    Fix file permissions for the specified folders.

    Args:
        folders (list): A list of folders to fix permissions for.

    Returns:
        str: A string indicating the completion status of the function.

    Raises:
        Exception: If there is an error in the file permissions subprocess.

    """
    error = False
    logger.info(
        "\n\n=========================== START PERMISSIONS FIX ==========================="
    )
    for folder in folders:
        try:
            if any(
                keyword in folder for keyword in ["Isilon2", "ng-editorial", "fsis3"]
            ):
                continue
            else:
                os.chdir(script_root)
                captured_output = subprocess.run(
                    ["sudo", "./permissions_fix.sh", folder],
                    shell=False,
                    capture_output=True,
                    universal_newlines=True,
                    check=True,
                    timeout=120,
                    bufsize=100,
                )
                logger.info(f"\n\\ {captured_output} \n\\ ")

        except Exception as e:
            logger.error(f"Error on file permissions subprocess: \n {e}")
            error = True

    logger.info(
        "\n=========================== END PERMISSIONS FIX ===========================\n"
    )
    return "done"


if __name__ == "__main__":
    folders_to_fix = []  # Add the folders you want to fix permissions for
    fix_permissions(folders_to_fix)
