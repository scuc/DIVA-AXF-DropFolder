#! /usr/bin/env python3

import logging
import os
import time

import config
import check_dir_size as checksize
import filepath_mods as fpmod

config = config.get_config()
archive_f = config['paths']['mac_archive_folder']
drop_f = config['paths']['mac_dropfolder']
divaname = config['paths']['DIVAName']

logger = logging.getLogger(__name__)


def archiving_check(): 
    """
    Check the number of sets in _archiving, pause the script if count exceeds the limit.
    """
    cycle_count = 0 
    while True: 
        try: 
            alist = [a for a in os.listdir(
                archive_f) if os.path.isdir(os.path.join(archive_f, a)) and
                a != a.endswith(".mdf")]
            
            alist_count = len(alist)

            if alist_count > 10: 
                print(f"LIST LENGTH:  {alist_count} ")
                cycle_count += 1
                print(f"CYCLE COUNT:  {cycle_count} ")

                if cycle_count == 0: 
                    pause_msg = f"Fold Sets archiving: {alist_count}\n\
                                  Script will pause while archive queue clears."
                elif cycle_count%5 == 0:
                    pause_msg = f"Archiving Queue paused for: {cycle_count*300} seconds \n\
                                  Current active archive count: {alist_count}\n\
                                  Processing will resume when the active archive count drops."
                else:
                    pause_msg = f"Current active archive count: {alist_count}"
                    pass
                logger.info(pause_msg)
                time.sleep(300)
                continue
            else: 
                queue_clear_msg = f"Archiving Queue has cleared. \n\
                                    Current active archive count: {alist_count}\n\
                                    Processing of new sets was paused for a total of {cycle_count*300}.seconds.\n\
                                    The script will now continue."
                logger.info(queue_clear_msg)
                return 

        except Exception as e:
            logger.exception(e)
            break


if __name__ == '__main__':
    archiving_check()
