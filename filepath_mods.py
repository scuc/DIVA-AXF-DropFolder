#! /usr/bin/env python3

import logging
import os
import re
import shutil

from pathlib import Path

import config

logger = logging.getLogger(__name__)

config = config.get_config()

archive_error_f = [
                os.path.join(config['paths']['mac_root_path']['storage01'], config['paths']['error']), 
                os.path.join(config['paths']['mac_root_path']['storage02'], config['paths']['error']),
                ]

def check_pathname(path):
    """
    Check each path recursively, and elminiate any illegal characters.
    """
    #print("STARTING")
    total_dir_change = 0

    while True:

        try:
            dir_count = 0
            dir_chng = False
            dir_chng_count = 0

            for root, dirs, files in os.walk(path):
                
                for name in dirs:
                    # print(f"DIRS:    {dirs}")
                    pathname = os.path.join(root, name)
                    dir_count += 1
                    cleanname = makeSafeName(root, name)

                    if cleanname == False: 
                        name_err_msg = f"Error (E1) cleaning filename, moving to Archive_Error - {pathname}"
                        logger.info(name_err_msg)
                        move_to_archive_error(path)
                        return
            
                    if len(cleanname) != len(name):
                        dir_chng_count += 1
                        continue
                    else:
                        pass

            if dir_chng_count != 0:
                total_dir_change = dir_chng_count + total_dir_change
                continue
            else: 
                break

        except Exception as e:
            dir_walk_msg = f"Exception on DIR Walk: \n {e}"
            logger.error(dir_walk_msg)
            break

    try: 
        file_count = 0
        ds_count = 0           
        file_chng_count = 0
        for root, dirs, files in os.walk(path):
            for name in files:
                pathname = os.path.join(root, name)
                file_count += 1
                if pathname.endswith(".DS_Store"):
                    os.remove(pathname)
                    ds_count += 1
                    continue
                else:
                    cleanname = makeSafeName(root, name)
                    
                    if cleanname == False:
                        name_err_msg = f"Error(E2) cleaning filename, moving to Archive_Error - {pathname}"
                        logger.info(name_err_msg)
                        move_to_archive_error(path)
                        return

                    if len(cleanname) != len(name):
                        file_chng_count += 1
                    else:
                        pass

    except Exception as e:
        file_walk_msg = f"Exception on FILE Walk: \n {e}"
        logger.error(file_walk_msg)


    total_dir_msg = f"{dir_count} sub-directories in project {os.path.basename(path)}"
    total_files_msg = f"{file_count - ds_count} files in project {os.path.basename(path)}"
    dir_name_change_msg = f"{total_dir_change} directory names changed to remove illegal characters."
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

    try: 
        # print("START MAKE SAFE")
        if len(remove_chars) != 0: 

            cleanname = name.replace("&", "and")
            cleanname = cleanname.replace(":", "_")
            cleanname = cleanname.replace("=", "_")
            cleanname = "".join([x for x in cleanname if x not in illegalchars])

            p = Path(os.path.join(root,name))
            cleanp = Path(os.path.join(root,cleanname))
            p.rename(cleanp)

            pathname_msg = f"\n\
            {remove_chars} - illegal characters removed from pathname.\n\
            name:     {name} \n\
            clean name:     {cleanname} \n "
            logger.info(pathname_msg)

        else:
            cleanname = name

    except Exception as e:
        make_safe_msg = f"Exception raised on attempt to clean illegal characters: \n {e}"
        print(f"EXCEPTION:   {e}  ")
        logger.error(make_safe_msg)
        cleanname = False

    return cleanname


def move_to_archive_error(path):
    error_f = os.path.join(path[:28], "_AXF_Archive_ERROR/")
    shutil.move(path, error_f)
    return 



if __name__ == '__main__':
    check_pathname("/Volumes/Quantum3/__Archive/_AXF_Archive_ERROR/88023_074995_BiteStingKill_MastersOfTheCoasts_EM_ALL_WAV")



