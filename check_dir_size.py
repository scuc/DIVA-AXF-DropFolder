#! /usr/bin/env python3

import logging
import os
import time

logger = logging.getLogger(__name__)


def check_dir_size(dpath):
    """
    Walk the dir of a potential archive and check to make sure the dir is not growing.
    If so, wait 5 seconds and check again, if not return and create the .csv file.
    size_value:
    0 = Object is not growing, proceed
    1 = Object is growing, and has exceeded wait time, move on.
    """
    checked_size = 0
    total_size = 0
    check_count = 0

    begin_size_chk_msg = (
        f"Checking to see if object is still growing for:  {os.path.basename(dpath)}"
    )
    logger.info(begin_size_chk_msg)

    while True:
        try:
            checked_size = os.path.getsize(dpath)
            if checked_size != total_size:
                total_size = checked_size

            check_count += 1

            growing_msg = f"Size still growing for:  {os.path.basename(dpath)}"
            pause_msg = f"Waiting 10 seconds to remeasure size."
            chk_count_msg = f"Check Count = {check_count}"

            if total_size != checked_size and check_count < 3:

                logger.info(chk_count_msg)
                logger.info(growing_msg)
                logger.info(pause_msg)
                log_sizecheck_msg(dpath, checked_size, total_size)

                time.sleep(10)
                continue

            elif total_size != checked_size and check_count == 3:
                size_value = 1
                count_end_msg = f"{os.path.basename(dpath)} - object still growing after 90sec, moving to next object for archive."
                logger.info(chk_count_msg)
                logger.info(count_end_msg)
                log_sizecheck_msg(dpath, checked_size, total_size)
                break

            elif total_size == checked_size and check_count > 1:
                notgrowing_msg = f"{os.path.basename(dpath)}  is ready for archive. End of size check."
                logger.info(chk_count_msg)
                logger.info(notgrowing_msg)
                log_sizecheck_msg(dpath, checked_size, total_size)
                size_value = 0
                break

        except Exception as e:
            logger.exception(e)
            if OSError:
                size_value = 3
            return size_value

    return size_value


def log_sizecheck_msg(dpath, checked_size, total_size):
    size_chk_msg = f"\n\
    ================================================================\n\
                Checking Size for: {os.path.basename(dpath)}\n\
                Total Dir Size at Start: {checked_size}\n\
                Total Dir Size at Finish: {total_size}\n\
    ================================================================\
    "
    print(size_chk_msg)
    logger.info(size_chk_msg)
    return


if __name__ == "__main__":
    check_dir_size("/Volumes/Quantum3/__Archive/_AXF_Archive_ERROR/88023_074995_GFX")
