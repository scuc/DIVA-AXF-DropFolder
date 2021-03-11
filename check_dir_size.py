#! /usr/bin/env python3

import logging
import os
import time

logger = logging.getLogger(__name__)


def check_dir_size(dpath):
    """
    Walk the dir of a potential archive and check to make sure the dir is not growing. 
    If so, wait 5 seconds and check again, if not return and create the .csv file. 
    directory_value: 
    0 = Dir is not growing, proceed
    1 = Dir is growing, and has exceeded wait time, move on. 
    """
    checked_size = 0
    total_size = 0
    check_count = 0
    
    begin_size_chk_msg = f"Checking to see if directory is still growing for:  {os.path.basename(dpath)}"
    logger.info(begin_size_chk_msg)

    while True:
        try:     
            for dirpath, dirnames, filenames in os.walk(dpath):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
                
            size_chk_msg = f"\n\
            ================================================================\n\
                        Checking Size for Dir: {os.path.basename(dpath)}\n\
                        Total Dir Size at Start: {checked_size}\n\
                        Total Dir Size at Finish: {total_size}\n\
            ================================================================\
            "
            logger.info(size_chk_msg)
            check_count += 1

            dir_growing_msg = f"Dir size is still growing for:  {os.path.basename(dpath)}"
            pause_message = f"Waiting 10 seconds to remeasure dir size."
            chk_count_message = f"Check Count = {check_count}"

            if (total_size != checked_size
                and check_count < 3):

                checked_size = total_size
                total_size = 0

                logger.info(chk_count_message)
                logger.info(pause_message)

                time.sleep(10)
                continue

            elif (total_size != checked_size
                and check_count == 3):
                directory_value = 1
                count_end_msg = f"{os.path.basename(dpath)} - dir is still growing after 90sec, moving to next dir for archive."
                logger.info(chk_count_message)
                logger.info(count_end_msg)
                break

            elif (total_size == checked_size
                  and check_count > 1):
                dir_notgrowing_msg = f"{os.path.basename(dpath)}  is ready for archive. End of size check."
                logger.info(chk_count_message)
                logger.info(dir_notgrowing_msg)
                directory_value = 0
                break
            break
        except Exception as e:
            logger.exception(e)
            if OSError:
                dir_value = 3
                return dir_value
            break

    return directory_value


if __name__ == '__main__':
    check_dir_size(dpath)
