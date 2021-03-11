#! /usr/bin/env python3
import csv
import logging
import os
import re
import shutil
import time

from pathlib import Path
from sys import platform

import config
import archive_queue as aqueue
import check_dir_size as checksize
import filepath_mods as fpmod
import permissions_fix as permissions

config = config.get_config()
archive_f_mac = config['paths']['mac_archive_folder'] #script is executed from a mac
archive_f_win = config['paths']['win_archive_folder'] #diva servers are Win, use UNC to view files.
drop_f = config['paths']['mac_dropfolder']
obj_category = config['paths']['DIVA_Obj_Category']
source_dest = config['paths']['DIVA_Source_Dest']
archive_error_f = config['paths']['mac_archive_error_folder']

logger = logging.getLogger(__name__)


def create_csv():
    """
    Check a watch folder for directory sets to archive. 
    Walk through each directory set and build a list
    of file/folder paths to archive. Use the path list
    to write a .csv file that is used as the trigger for
    the DIVA archive job. 
    """

    for f in Path(drop_f).glob('*.csv'):
        try:
            f.unlink()
        except OSError as e:
            unlink_error_msg = f"Error Removeing old .CSV: {f}: {e.strerror}"
            logger.error(unlink_error_msg)

    queue_status = aqueue.archiving_check()

    if queue_status != 0:
        return
    else:
        pass

    """
    create a list of directories in the watch folder, check to see
    if the same directories are not already present in _archiving and
    _incomplete. 
    """

    dlist = [d for d in os.listdir(
        drop_f) if os.path.isdir(os.path.join(drop_f, d)) and
        d not in ["_archiving", "_incomplete"]]

    if len(dlist) == 0:
        empty_msg = f"No new dir for archiving."
        logger.info(empty_msg)
        return
    else:
        dlist_msg = f"New directories for archiving: {dlist}"
        logger.info(dlist_msg)

        if platform == "darwin":
            permissions.chmod_chown()

        t = time.time()
        date = time.strftime('%Y%m%d%H%M', time.localtime(t))
        csv_doc = f"{date}_diva.csv"

        movelist = []
        movelist.append(os.path.join(drop_f, csv_doc))

        os.chdir(drop_f)

        with open(f"{csv_doc}", mode='w', newline='', encoding='utf-8-sig') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')

            count = 0
            for d in dlist:
                dpath = os.path.join(drop_f, d)
                dir_value = checksize.check_dir_size(dpath)

                if dir_value == 1:
                    continue
                
                elif dir_value == 3: 
                    oserror_msg = f"OSError found, likely illegal characters, moving directory to _AXF_ARCHIVE_ERROR"
                    logger.error(oserror_msg)
                    shutil.move(dpath, archive_error_f)
                    continue

                else:
                    fpath = fpmod.check_pathname(dpath)

                    if count == 0:
                        csv_writer.writerow(
                            ["object name", "object category", "source destination", "root path", "list of files"])

                    if count == 10:
                        max_count_msg = f"Maximum number of folder submissions reached for this archive cycle."
                        logger.info(max_count_msg)
                        break

                    csv_writer.writerow(
                        [f"{d}", obj_category, source_dest, archive_f_win, f"{d}/*"])
                    movelist.append(dpath)

                count += 1

            csv_file.close()

            new_csv_msg = f"New .csv file created: {csv_doc}"
            logger.info(new_csv_msg)

            print(f"============= MOVE LIST: {movelist}")
            moved_list = move_to_checkin(movelist)
            move_msg = f"The following directories have been moved into the archiving location: \n{moved_list}"
            logger.info(move_msg)


def move_to_checkin(movelist):
    """
    Move files and dir in the movelist from the drop folder to the archive location.
    """
    moved_list = []
    for x in movelist:
        arch_check = os.path.basename(x)
        try:
            if x.startswith("."):
                pass
            if os.path.exists(os.path.join(archive_f_mac, arch_check)):
                skip_msg = f"{arch_check} already exists in this location, skipping"
                logger.info(skip_msg)
                pass
            else:
                shutil.move(x, archive_f_mac)
                moved_list.append(arch_check)
        except Exception as e:
            move_excp_msg = f"\n\
            Exception raised on moving {x}.\n\
            Error Message:  {str(e)} \n\
            "
            logger.error(move_excp_msg)

    print(f"MOVED LIST - LINE#138 = {moved_list}")
    return moved_list


if __name__ == '__main__':
    create_csv()
