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

    while True:
        try:
            dir_count = 0
            for root, dirs, files in os.walk(path):
                dir_chng_count = 0
                for name in dirs:
                    # print(f"DIRS:    {dirs}")
                    pathname = os.path.join(root, name)
                    dir_count += 1
                    cleanname = makeSafeName(root, name)
                    # print(f"DIR NAME:   {pathname}")
                    if len(cleanname) != len(pathname):
                        dir_chng_count += 1
                        continue
                    else:
                        pass
            if dir_chng_count != 0: 
                continue
            else: 
                break

        except Exception as e:
            dir_walk_msg = f"Exception on DIR Walk: \n {e}"
            logger.error(dir_walk_msg)
            continue

    try: 
        file_count = 0
        ds_count = 0
        for root, dirs, files in os.walk(path):
            file_chng_count = 0
            for name in files:
                pathname = os.path.join(root, name)
                # print(f"FILENAME:   {pathname}")
                file_count += 1
                if pathname.endswith(".DS_Store"):
                    os.remove(pathname)
                    ds_count += 1
                    continue
                else:
                    cleanname = makeSafeName(root, name)
                    if len(cleanname) != len(pathname):
                        file_chng_count += 1
                    else:
                        pass
    except Exception as e:
        file_walk_msg = f"Exception on FILE Walk: \n {e}"
        logger.error(file_walk_msg)


    total_dir_msg = f"{dir_count} sub-directories in project {os.path.basename(path)}"
    total_files_msg = f"{file_count - ds_count} files in project {os.path.basename(path)}"
    dir_name_change_msg = f"{dir_chng_count} directory names changed to remove illegal characters."
    file_name_change_msg = f"{file_chng_count} file names changed to remove illegal characters."
    rm_msg = f"{ds_count} .DS_Store files removed from dir before archive."
    
    logger.info(total_dir_msg)
    logger.info(total_files_msg)
    logger.info(dir_name_change_msg)
    logger.info(file_name_change_msg)
    logger.info(rm_msg)
    return 


def makeSafeName(root, name):
    """
    Check a path name against a list of illegal characters, remove any found. 
    """

    illegalchars = ["@", ":", "*", "?", "!", '"', "'", "<", ">", "|", "&", "#", "%","$", "~", "+", "="]
    remove_chars = [x for x in name if x in illegalchars]

    if len(remove_chars) != 0: 

        cleanname = name.replace("&", " and ")
        cleanname = cleanname.replace(":", " ")
        cleanname = cleanname.replace("=", " ")
        cleanname = "".join([x for x in cleanname if x not in illegalchars])

        p = Path(os.path.join(root,name))
        cleanp = Path(os.path.join(root,cleanname))
        p.rename(cleanp)

        pathname_msg = f"\n\
        {remove_chars} - illegal characters removed from pathname.\n\
        pathname:     {name} \n\
        safe pathname:     {cleanname} \n "
        logger.info(pathname_msg)

    else:
        cleanname = name
    
    return cleanname


if __name__ == '__main__':
    check_pathname(path)



