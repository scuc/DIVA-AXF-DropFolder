#! /usr/bin/env python3

import logging
import os
import shutil
import time

import config
import check_dir_size as checksize
import filepath_mods as fpmod

config = config.get_config()
archive_error_f = [
                os.path.join(config['paths']['mac_root_path']['storage01'], config['paths']['error']), 
                os.path.join(config['paths']['mac_root_path']['storage02'], config['paths']['error']),
                os.path.join(config['paths']['mac_root_path']['storage03'], config['paths']['error']),
                ]
drop_folders = [
                os.path.join(config['paths']['mac_root_path']['storage01'], config['paths']['drop_folder']), 
                os.path.join(config['paths']['mac_root_path']['storage02'], config['paths']['drop_folder']),
                os.path.join(config['paths']['mac_root_path']['storage03'], config['paths']['drop_folder']),
                ]
archive_folders = [
                os.path.join(config['paths']['mac_root_path']['storage01'], config['paths']['archiving']), 
                os.path.join(config['paths']['mac_root_path']['storage02'], config['paths']['archiving']),
                os.path.join(config['paths']['mac_root_path']['storage03'], config['paths']['archiving']),
                ]

logger = logging.getLogger(__name__)


def get_archiving_list():
    """
    Check all Archive folder locations and build a list of everything that is still archiving. 
    """
    archiving_list = []
    for x in archive_folders:
        alist = [d for d in os.listdir(x) 
        if os.path.isdir(os.path.join(x, d)) and
        not d.startswith(".")]
        archiving_list = archiving_list + alist
    return archiving_list


def archiving_check(): 
    """
    Check the number of sets in each _archiving dir, pause the script if count exceeds the limit.
    """
    cycle_count = 0 

    while True: 
        try:  
            archiving_list = get_archiving_list()
            alist_count = len(archiving_list)

            if alist_count > 10: 

                if cycle_count == 0: 
                    pause_msg = f"Folder Sets archiving: {alist_count}\n\
                                  Script will pause while archive queue clears."
                elif (cycle_count%5 == 0
                    and cycle_count != 30):
                    pause_msg = f"Archiving Queue paused for: {cycle_count*300} seconds \n\
                                  Current active archive count: {alist_count}\n\
                                  Processing will resume when the active archive count drops."
                elif cycle_count == 30: 
                    pause_msg = f"Archiving Queue paused for: {cycle_count*300} seconds \n\
                                Current active archive count: {alist_count}\n\
                                STOPPING ARCHIVE ATTEMPT, will try again later"
                    queue_status = 1
                    logger.info(pause_msg)
                    return queue_status
                else:
                    pause_msg = f"Current active archive count: {alist_count}"
                    pass
                cycle_count += 1
                logger.info(pause_msg)
                time.sleep(90)
                continue
            else: 
                queue_clear_msg = f"Archiving Queue status. \n\
                                    Current active archive count: {alist_count}\n\
                                    Processing of new sets was paused for a total of {cycle_count*300}.seconds.\n\
                                    Archive submission will proceed."
                logger.info(queue_clear_msg)
                queue_status = 0
                return queue_status

        except Exception as e:
            logger.exception(e)
            break


if __name__ == '__main__':
    archiving_check()
