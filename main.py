import logging

#! /usr/bin/env python3
import logging.config
import os
from datetime import datetime
from sys import platform
from time import localtime, strftime

import yaml

import check_root_paths as crp
import config
import dropfolder_check_csv as dfc
import permissions_fix as permissions


def set_logger():
    """
    Setup logging configuration
    """
    script_root = config.get_config()["paths"]["script_root"]
    path = os.path.join(script_root, "logging.yaml")

    with open(path, "rt") as f:
        config = yaml.safe_load(f.read())

        # get the file name from the handlers, append the date to the filename.
        for i in config["handlers"].keys():
            if "filename" in config["handlers"][i]:
                log_filename = config["handlers"][i]["filename"]
                base, extension = os.path.splitext(log_filename)
                today = datetime.today()

                log_filename = f"{base}_{today.strftime('%Y%m%d')}{extension}"
                config["handlers"][i]["filename"] = log_filename

        logger = logging.config.dictConfig(config)

    return logger


def main():
    """
    This function is the entry point of the DIVA Archive Script.
    It performs various tasks related to archiving and logging.

    Returns:
        None
    """

    logger = set_logger()

    date_start = strftime("%A, %d. %B %Y %I:%M%p", localtime())

    start_msg = f"""
    ================================================================
                DIVA Archive Script - Start
                    {date_start}
    ================================================================
    """

    logger.info(start_msg)

    root_paths = crp.check_root_paths()

    if platform == "darwin" and root_paths is not False:
        permissions.fix_permissions(config.get_config()["paths"]["mac_root_path"])

    dfc.create_csv()

    date_end = strftime("%A, %d. %B %Y %I:%M%p", localtime())

    complete_msg = f"""
    ================================================================
                DIVA WatchFolder Check - Complete
                    {date_end}
    ================================================================
    """
    logger.info(complete_msg)


if __name__ == "__main__":
    main()
