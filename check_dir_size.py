#! /usr/bin/env python3

import logging
import os
import time

logger = logging.getLogger(__name__)


def check_dir_size(dpath):
    """
    Walk the dir of a potential archive and check to make sure the dir is not growing. 
    If so, wait 5 seconds and check again, if not return and create the .mdf file. 
    directory_value: 
    0 = Dir is not growing, proceed
    1 = Dir is growing, and has exceeded wait time, move on. 
    """
    checked_size = 0
    total_size = 0
    
    begin_size_chk_msg = f"Checking to see if directory is still growing for:  {os.path.basename(dpath)}"
    logger.info(begin_size_chk_msg)

    while True:
        check_count = 0
        try:     
            for dirpath, dirnames, filenames in os.walk(dpath):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
                
            size_chk_msg = f"\n\n\
            ================================================================\n \
                        Checking Size for Dir: {os.path.basename(dpath)}\n\
                        Total Dir Size at Start: {checked_size}\n\
                        Total Dir Size at Finish: {total_size}\n\
            ================================================================\n\
            \n"
            logger.info(size_chk_msg)
            check_count += 1

            if (total_size != checked_size
                and check_count <= 6):

                checked_size = total_size
                total_size = 0

                dir_growing_msg = f"Dir size is still growing for:  {os.path.basename(dpath)}"
                pause_message = f"Wating 30 seconds to remeasure dir size."
                chk_count_message = f"Check Count = {check_count}"
                logger.info(chk_count_message)
                logger.info(dir_growing_msg)
                logger.info(pause_message)

                time.sleep(30)

                continue
            elif check_count == 6: 
                directory_value = 1
                count_end_msg = f"{os.path.basename(dpath)} - dir is still growing after 3min, moving to next dir for archive."
                logger.info(count_end_msg)
                break
            else:
                dir_notgrowing_msg = f"{os.path.basename(dpath)}  is ready for archive. End of size check."
                logger.info(dir_notgrowing_msg)
                directory_value = 0
                break
            break
        except Exception as e:
            logger.exception(e)
            break

    return directory_value


if __name__ == '__main__':
    check_dir_size(dpath)
