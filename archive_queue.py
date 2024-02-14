import logging
import os
import time
from time import localtime, strftime

import api_DIVA as api
import config

config = config.get_config()


script_root = config["paths"]["script_root"]
mac_root_folders = config["paths"]["mac_root_path"]
drop_folders = [
    os.path.join(x, config["paths"]["drop_folder"]) for x in mac_root_folders
]
archive_error_f = [os.path.join(x, config["paths"]["error"]) for x in mac_root_folders]
archive_folders = [
    os.path.join(x, config["paths"]["archiving"]) for x in mac_root_folders
]


logger = logging.getLogger(__name__)


def get_archiving_list():
    """
    Check all Archive folder locations and build a list of everything that is still archiving.
    """
    archiving_list = []
    for x in archive_folders:
        alist = [d for d in os.listdir(x) if not d.startswith(".")]
        archiving_list = archiving_list + alist
    return archiving_list


def archiving_check():
    """
    Check the number of active archives, pause the script if count exceeds the set limit.
    """
    cycle_count = 0
    startDateTime = f"{strftime('%Y-%m-%d', localtime())} 00:00:00"

    while True:
        try:
            archive_jobs = api.get_requests(startDateTime)

            if len(archive_jobs) > 15:

                if cycle_count == 0:
                    pause_msg = f"Objects archiving: {archive_jobs}\n\
                                  Script will pause while archive queue clears."
                elif cycle_count % 5 == 0 and cycle_count != 30:
                    pause_msg = f"Archiving Queue paused for: {cycle_count*300} seconds \n\
                                  Current active archive count: {archive_jobs}\n\
                                  Processing will resume when the active archive count drops."
                elif cycle_count == 30:
                    pause_msg = f"Archiving Queue paused for: {cycle_count*300} seconds \n\
                                Current active archive count: {archive_jobs}\n\
                                STOPPING ARCHIVE ATTEMPT, will try again later"
                    queue_status = 1
                    logger.info(pause_msg)
                    return queue_status
                else:
                    pause_msg = f"Current active archive count: {archive_jobs}"
                    pass
                cycle_count += 1
                logger.info(pause_msg)
                time.sleep(90)
                continue
            else:
                queue_clear_msg = f"Archiving Queue status. \n\
                                    Current active archive count: {archive_jobs}\n\
                                    Processing of new sets was paused for a total of {cycle_count*300}.seconds.\n\
                                    Archive submission will proceed."
                logger.info(queue_clear_msg)
                queue_status = 0
                return queue_status

        except Exception as e:
            logger.exception(e)
            break


if __name__ == "__main__":
    archiving_check()
