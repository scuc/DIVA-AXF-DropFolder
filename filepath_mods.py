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

    try:
        for root, dirs, files in os.walk(path):
            dir_list = []
            for name in dirs:
                print(f"DIRS:    {dirs}")
                # pathname = os.path.join(root, name)
                dir_count += 1
                safe_pathname = makeSafeName(root, name)
                # print(f"DIR NAME:   {pathname}")

    except Exception as e:
        print(f"Exception on DIR Walk: \n {e}")

    try: 
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
                    safe_pathname = makeSafeName(root, name)
    except Exception as e:
        print(f"Exception on FILE Walk: \n {e}")


    total_dir_msg = f"{dir_count} sub-directories in project {os.path.basename(path)}"
    total_files_msg = f"{file_count - ds_count} files in project {os.path.basename(path)}"
    rm_msg = f"{ds_count} .DS_Store files removed from dir before archive."
    
    logger.info(total_dir_msg)
    logger.info(total_files_msg)
    logger.info(rm_msg)
    return 


def makeSafeName(root, name):
    """
    Check a path name against a list of illegal characters, remove any found. 
    """

    illegalchars = ["@", ":", "*", "?", '"', "'", "<", ">", "|", "&", "#", "%", "(", ")","$", "~", "+", "="]
    cleanname = "".join([x for x in name if x not in illegalchars])

    if len(name) != len(cleanname): 
        p = Path(os.path.join(root,name))
        cleanp = Path(os.path.join(root,cleanname))
        p.rename(cleanp)
        char_count = len(name) - len(cleanname)
        pathname_msg = f"\n\
        {char_count} illegal characters removed from pathname.\n\
        pathname:     {name} \n\
        safe pathname:     {cleanname} \n "
        clean_count = 1
        logger.info(pathname_msg)
    else:
        cleanp = name 
    
    return


if __name__ == '__main__':
    check_pathname(path)



