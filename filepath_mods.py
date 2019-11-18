#! /usr/bin/env python3

import logging
import os
import re

from pathlib import Path

logger = logging.getLogger(__name__)


def check_pathname(path):
    """
    Check each path recursively, and elminiate any illegal characters.
    """
    dir_count = 0
    file_count = 0
    ds_count = 0

    for root, dirs, files in os.walk(path):
        for name in dirs:
            pathname = os.path.join(root, name)
            dir_count += 1
            safe_pathname = makeSafeName(pathname)
            # print(f"DIR NAME:   {pathname}")

    for root, dirs, files in os.walk(path):
        for name in files:
            pathname = os.path.join(root, name)
            # print(f"FILENAME:   {pathname}")
            file_count += 1
            if pathname.endswith(".DS_Store"):
                os.remove(pathname)
                ds_count += 1
                continue
            else:
                safe_pathname = makeSafeName(pathname)

    total_dir_msg = f"{dir_count} sub-directories in project {os.path.basename(path)}"
    total_files_msg = f"{file_count - ds_count} files in project {os.path.basename(path)}"
    rm_msg = f"{ds_count} .DS_Store files removed from dir before archive."
    
    logger.info(total_dir_msg)
    logger.info(total_files_msg)
    logger.info(rm_msg)
    return 


def makeSafeName(pathname):
    """
    Check a path name against a list of illegal characters, remove any found. 
    """

    illegalchars = ["@", ":", "*", "?", '"', "'", "<", ">", "|", "&", "#", "%", "(", ")","$", "~", "+", "="]
    cleanpath = "".join([x for x in pathname if x not in illegalchars])

    if len(pathname) != len(cleanpath): 
        p = Path(pathname)
        cleanp = Path(cleanpath)
        p.rename(cleanp)
        char_count = len(pathname) - len(cleanpath)
        pathname_msg = f"\n\
        {char_count} illegal characters removed from pathname.\n\
        pathname:     {pathname} \n\
        safe pathname:     {cleanpath} \n "
        clean_count = 1
        logger.info(pathname_msg)
    else:
        cleanp = pathname 
    
    return cleanp


if __name__ == '__main__':
    check_pathname(path)



