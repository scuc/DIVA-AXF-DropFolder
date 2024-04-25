import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from time import localtime, strftime

import api_DIVA as api
import config as cfg

config = cfg.get_config()
logger = logging.getLogger(__name__)

script_root = config["paths"]["script_root"]
mac_root_folders = config["paths"]["mac_root_path"]
drop_folders = [
    os.path.join(x, config["paths"]["drop_folder"]) for x in mac_root_folders
]


def check_job_duration():

    for job in dropfolder_list:

        with open("dropfolder_jobs.json", "rt+") as f:
            contents = f.readlines()
            f.close
        with open("dropfolder_jobs.json", "wt+") as f:
            for line in contents:
                if line.strip("\n") != vantage_job_id:
                    f.write(line)
                else:
                    timenow = datetime.datetime.today()
                    timestamp = (timenow.strftime("%Y-%m-%d, %H:%M:%S"),)
                    new_line = line.replace(
                        vantage_job_id,
                        f"[ {timestamp} - Upload Failed for job id: {vantage_job_id} ]",
                    )
                    f.write(new_line)
                    cleanup_msg = f"Adstream Media Creation Failure - Job ID: {vantage_job_id}, Filename: {filename}"
                    logger.info(cleanup_msg)
            f.close


def getDuration(then, now=datetime.now()):

    duration = now - then
    duration_in_sec = duration.total_seconds()

    return duration_in_sec
