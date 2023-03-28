#! /usr/bin/env python3

import logging
import os
import re
import shutil
from collections import Counter
from pathlib import Path
from string import whitespace

import config
from check_obj_size import get_object_size as get_size

logger = logging.getLogger(__name__)

config = config.get_config()

script_root = config["paths"]["script_root"]
mac_root_folders = config["paths"]["mac_root_path"]
archive_error_f = [os.path.join(x, config["paths"]["error"]) for x in mac_root_folders]
archive_req_zip_f = [
    os.path.join(x, config["paths"]["requires_zip"]) for x in mac_root_folders
]


def check_pathname(path):
    """
    Check each path recursively, and elminiate any illegal characters.
    """

    total_dir_change = 0
    cleanname_total = Counter({"illegal_char_count": 0, "whitespace_count": 0})

    while True:
        try:
            dir_count = 0
            dir_chng = False
            dir_chng_count = 0

            for root, dirs, files in os.walk(path):

                for name in dirs:
                    pathname = os.path.join(root, name)
                    dir_count += 1
                    cleanname, cleanname_totals = makeSafeName(root, name)

                    cleanname_total.update(cleanname_totals)

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
        char_limit_count = 0
        validation_result = 0

        for root, dirs, files in os.walk(path):
            for name in files:
                pathname = os.path.join(root, name)
                file_count += 1
                if (
                    name.startswith(".DS_Store")
                    or name.startswith("._")
                    and os.stat(pathname).st_size < 5000
                ):
                    os.remove(pathname)
                    ds_count += 1
                    continue
                else:
                    cleanname, cleanname_totals = makeSafeName(root, name)

                    cleanname_total.update(cleanname_totals)

                    if cleanname == False:
                        name_err_msg = f"Error(E2) cleaning filename, moving to Archive_Error - {pathname}"
                        logger.info(name_err_msg)
                        move_to_archive_error(path)
                        return

                    if len(cleanname) != len(name):
                        file_chng_count += 1
                    else:
                        pass

                    if len(os.path.join(root, cleanname)) > 255:
                        illegal_path = os.path.join(root, cleanname)
                        char_limit_msg = f"Too many characters for Windows path (>255): \n {illegal_path} "
                        logger.info(char_limit_msg)
                        write_path_to_txt(path, illegal_path)
                        validation_result = 1
                        char_limit_count += 1
                    else:
                        pass

    except Exception as e:
        file_walk_msg = f"Exception on FILE Walk: \n {e}"
        logger.error(file_walk_msg)

    if char_limit_count > 0:
        move_to_archive_zip(path)
        mv_msg = f"{path} moved to _Archive_REQ_ZIP directory."
        logger.info(mv_msg)

    total_dir_msg = f"{dir_count} sub-directories in project {os.path.basename(path)}"
    total_files_msg = (
        f"{file_count - ds_count} files in project {os.path.basename(path)}"
    )
    dir_name_change_msg = (
        f"{total_dir_change} directory names changed to remove illegal characters."
    )
    file_name_change_msg = (
        f"{file_chng_count} file names changed to remove illegal characters."
    )
    char_limit_count_msg = (
        f"{char_limit_count} file paths that exceed the 255 Windows limit"
    )
    illegal_chars_msg = (
        f"{cleanname_total['illegal_char_count']} illegal characters were found."
    )
    whitespace_msg = f"{cleanname_total['whitespace_count']} whitespace characters removed from filenames."
    rm_msg = f"{ds_count} .DS_Store or ._ files removed from dir before archive."

    logger.info(total_dir_msg)
    logger.info(total_files_msg)
    logger.info(dir_name_change_msg)
    logger.info(file_name_change_msg)
    logger.info(char_limit_count_msg)
    logger.info(illegal_chars_msg)
    logger.info(whitespace_msg)
    logger.info(rm_msg)

    return validation_result


def makeSafeName(root, name):
    """
    Check a path name against a list of illegal characters, remove any found.
    """
    illegal_char_count = 0
    whitespace_count = 0

    illegalchars = [
        "@",
        ":",
        "*",
        "?",
        "!",
        '"',
        "'",
        "<",
        ">",
        "|",
        "&",
        "#",
        "%",
        "$",
        "~",
        "+",
        "=",
    ]
    illegal_char_count = len([x for x in name if x in illegalchars])

    try:
        # remove leading and trailing all whitespace and count number of subs
        cleanname = re.subn(r"^\s+|\s+$", "", name)
        whitespace_count = cleanname[1]

        p = Path(os.path.join(root, name))
        cleanp = Path(os.path.join(root, cleanname[0]))
        p.rename(cleanp)

        if illegal_char_count != 0:

            cleanname = name.replace("&", "_and_")
            cleanname = cleanname.replace(":", "_")
            cleanname = cleanname.replace("=", "_")
            cleanname = "".join([x for x in cleanname if x not in illegalchars])

        else:
            cleanname = name

    except Exception as e:
        make_safe_msg = (
            f"Exception raised on attempt to clean illegal characters: \n {e}"
        )
        logger.error(make_safe_msg)
        cleanname = False

    if illegal_char_count > 0 or whitespace_count > 0:

        pathname_msg = f"\n\
        {illegal_char_count} - illegal characters removed from pathname.\n\
        {whitespace_count} - whitespace characters removed from head and tail \n\
        name:  {name} \n\
        clean name:  {cleanname} \n "
        logger.info(pathname_msg)

    else:
        pass

    cleanname_totals = {
        "illegal_char_count": illegal_char_count,
        "whitespace_count": whitespace_count,
    }

    return cleanname, cleanname_totals


def move_to_archive_error(path):
    error_f = os.path.join(path[:28], "_Archive_ERROR/")
    shutil.move(path, error_f)
    return


def move_to_archive_zip(path):
    req_zip_f = os.path.join(path[:28], "_Archive_REQ_ZIP")
    shutil.move(path, req_zip_f)
    return


def write_path_to_txt(path, illegal_path):
    req_zip_f = os.path.join(path[:28], "_Archive_REQ_ZIP")
    os.chdir(req_zip_f)
    with open(os.path.basename(path) + ".txt", "a+") as f:
        f.write(illegal_path + "\n")
        f.close()
    return


if __name__ == "__main__":
    check_pathname()
