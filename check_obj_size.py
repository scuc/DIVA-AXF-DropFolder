#! /usr/bin/env python3

import logging
import os
import time

logger = logging.getLogger(__name__)


def check_obj_size(dpath):
    """
    Walk the dir of a potential archive and check to make sure the dir is not growing.
    If so, wait 5 seconds and check again, if not return and create the .csv file.
    size_value:
    0 = Object measured at size 0, move on.
    1 = Object is growing, and has exceeded wait time, move on.
    2 = Object size is > 0 and size is not growing, ready for archive.
    3 = Error encountered measuring dir size.
    """
    checked_size = 0
    total_size = 0
    check_count = 0

    begin_size_chk_msg = f"Size Check for:  {os.path.basename(dpath)}"
    logger.info(begin_size_chk_msg)

    while True:
        try:
            checked_size = get_object_size(dpath)

            if checked_size == 0:
                size_value = 0
                logger.info("Size measured as 0, skipping dir.")
                return size_value

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
                formatted_checked_size = get_size_format(checked_size)
                formatted_total_size = get_size_format(total_size)
                log_sizecheck_msg(dpath, formatted_checked_size, formatted_total_size)
                size_value = 2
                break

        except Exception as e:
            logger.exception(e)
            if OSError:
                size_value = 3
            return size_value

    return size_value


def get_object_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                try:
                    total += get_object_size(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def log_sizecheck_msg(dpath, formatted_checked_size, formatted_total_size):
    size_chk_msg = f"\n\
    ================================================================\n\
                Checking Size for: {os.path.basename(dpath)}\n\
                Total Dir Size at Start: {formatted_checked_size}\n\
                Total Dir Size at Finish: {formatted_total_size}\n\
    ================================================================\
    "
    logger.info(size_chk_msg)
    return


if __name__ == "__main__":
    check_obj_size("")
