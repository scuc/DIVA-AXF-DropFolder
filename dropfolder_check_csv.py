#! /usr/bin/env python3
import csv
import glob
import logging
import os
import re
import shutil
import time

from pathlib import Path
from sys import platform

import config
import api_DIVA as api
import archive_queue as aqueue
import check_dir_size as checksize
import filepath_mods as fpmod
import permissions_fix as permissions

config = config.get_config()

archive_error_f = [
                os.path.join(config['paths']['mac_root_path']['storage01'], config['paths']['error']), 
                os.path.join(config['paths']['mac_root_path']['storage02'], config['paths']['error']),
                ]
archive_f_win = [ #diva servers are Win, use UNC to view files.
                config['paths']['win_archive']['storage01'], 
                config['paths']['win_archive']['storage02'],
                ] 
drop_folders = [
                os.path.join(config['paths']['mac_root_path']['storage01'], config['paths']['drop_folder']), 
                os.path.join(config['paths']['mac_root_path']['storage02'], config['paths']['drop_folder']),
                ]
obj_category = config['DIVA_Obj_Category']
source_dest = [
                config['DIVA_Source_Dest']['storage01'],
                config['DIVA_Source_Dest']['storage02'],
                ]


logger = logging.getLogger(__name__)


def create_csv():
    """ 
    Check a watch folder for directory sets to archive. 
    Walk through each directory set and build a list
    of file/folder paths to archive. Use the path list
    to write a .csv file that is used as the trigger for
    the DIVA archive job. 
    """

    csv_count, f = get_csv_count()
    counter = 0
    while (csv_count != 0 and
           counter < 10):
        csv_msg = f"Counter:{counter}, CSV file still present in {f}, pausing script for 300sec."
        logger.info(csv_msg)
        time.sleep(300)
        counter += 1
        csv_count = get_csv_count()

        if (len(csv_count) != 0
            and counter == 10): 
            csv_msg = f"Counter:{counter}, CSV file still present in {f} after 50min, ending script."
            logger.info(csv_msg)
            return

    # for f in Path(drop_f).glob('*.csv')
    #     time.sleep(90)
    #     try:
    #         f.unlink()
    #     except OSError as e:
    #         unlink_error_msg = f"Error Removeing old .CSV: {f}: {e.strerror}"
    #         logger.error(unlink_error_msg)

    queue_status = aqueue.archiving_check()

    if queue_status != 0:
        return
    else:
        pass

    """
    for each watch folder, create a list of directories present, check to see
    if the same directories are not already present in _archiving and
    _incomplete. 
    """
    index = 0
    for folder in drop_folders: 
        volume_name = folder[9:17]
        check_df_msg = f"Checking drop folder on: {volume_name}"
        logger.info(check_df_msg)

        source_destination = source_dest[index]
        archive_f_windows = archive_f_win[index]

        df_delimiter_msg = f"\n\n====================== DROP FOLDER: {volume_name} =========================\n\\"
        logger.info(df_delimiter_msg)

        dir_list = [d for d in os.listdir(folder) 
            if os.path.isdir(os.path.join(folder, d)) and
            d not in ["_archiving", "_incomplete"]]
            # dlist = dlist + dir_list

        if len(dir_list) == 0:
            empty_msg = f"{folder[9:17]} = No new dir for archiving."
            logger.info(empty_msg)
            index += 1
            continue

        else:
            t = time.time()
            date = time.strftime('%Y%m%d%H%M', time.localtime(t))
            dedup_dlist = dedup_list(dir_list, date, folder)
            csv_doc = f"{date}_diva.csv"

            dlist_msg = f"New directories for archiving: {dedup_dlist}"
            logger.info(dlist_msg)

            movelist = []
            movelist.append(os.path.join(folder, csv_doc))

            os.chdir(folder)

        with open(f"{csv_doc}", mode='w', newline='', encoding='utf-8-sig') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')

            count = 0
            for d in dedup_dlist:
                dpath = os.path.join(folder, d)
                dir_value = checksize.check_dir_size(dpath)
                
                if dir_value == 1:
                    continue
                
                fpath = fpmod.check_pathname(dpath)

                if dir_value == 3: 
                    oserror_msg = f"OSError found, likely illegal characters, unable to correct, moving to ERROR folder."
                    logger.error(oserror_msg)
                    shutil.move(dpath, )

                else:
                    if count == 0:
                        csv_writer.writerow(
                            ["object name", "object category", "source destination", "root path", "list of files"])

                    if count == 10:
                        max_count_msg = f"Maximum number of folder submissions reached for this archive cycle."
                        logger.info(max_count_msg)
                        break

                    csv_writer.writerow(
                        [f"{d}", obj_category, source_destination, archive_f_windows, f"{d}/*"])
                    movelist.append(dpath)

                count += 1

            csv_file.close()

            new_csv_msg = f"New .csv file created: {csv_doc}"
            logger.info(new_csv_msg)

            moved_list = move_to_checkin(movelist, folder)
            move_msg = f"Directories moved into archiving on {volume_name}: \n{moved_list}"
            logger.info(move_msg)
        index += 1


def get_csv_count():
    csv_count = 0
    for f in drop_folders:
        os.chdir(f)
        csv = glob.glob('*.csv', recursive=True)
        csv_count += len(csv)
    return csv_count, f


def dedup_list(dir_list, date, folder):
    """
    check list of directories against the DIVA DB, look for duplicates and remove from list
    """
    dedup_dlist = []
    duplicates = []
    for d in dir_list: 
        try: 
            archive_object = os.path.join(folder,d)
            duplicate = api.api_file_check(d)

            if duplicate == True:
                duplicates.append(d)

            elif duplicate == "error": 
                dup_err_msg = f"Error returned on duplicate check, moving to Archive Error: {d}"
                logger.error(dup_err_msg)
                shutil.move(archive_object, os.path.join(folder, "_AXF_Archive_ERROR")) 
            else:
                dedup_dlist.append(d)
        except Exception as e: 
            dup_excp_msg = f"Exception raised on Duplicate check: \n {e}"
            logger.error(dup_excp_msg)

    dedup_dlist_msg = f"New dir list after duplicates removed: {dedup_dlist}"
    logger.info(dedup_dlist_msg)

    duplicates_msg = f"Duplicates detected: {duplicates}"
    logger.info(duplicates_msg)
    
    dup_rename(duplicates, date, folder)

    return dedup_dlist


def dup_rename(duplicates, date, folder):
    #if dir by the same name already exisits in DIVA, append dir name with datetime stamp.
    try:
        for dup in duplicates:
            archive_object = os.path.join(folder, dup) 
            arch_obj_dt = f"{archive_object}_{date}"
            obj_rename_msg = f"Duplicate object, renamed:  {arch_obj_dt}"
            logger.info(obj_rename_msg)
            if arch_obj_dt is None: 
                continue
            else:
                os.rename(archive_object, arch_obj_dt)

    except Exception as e:
        rename_excp_msg = f"\n\
        Exception raised on dup rename {dup}.\n\
        Error Message:  {str(e)} \n\
        "
        logger.error(rename_excp_msg)  

    return 


def move_to_checkin(movelist, dropfolder):
    """
    Move files and dir in the movelist from the drop folder to the archive location.
    """
    moved_list = []
    for x in movelist:
        proj_folder = os.path.basename(x)
        try:
            if x.startswith("."):
                pass
            if os.path.exists(os.path.join(dropfolder, "_archiving", proj_folder)):
                skip_msg = f"{proj_folder} already exists in this location, skipping"
                logger.info(skip_msg)
                pass
            else:
                shutil.move(x, os.path.join(dropfolder,"_archiving"))
                moved_list.append(proj_folder)
        except Exception as e:
            move_excp_msg = f"\n\
            Exception raised on moving {x}.\n\
            Error Message:  {str(e)} \n\
            "
            logger.error(move_excp_msg)

    return moved_list


if __name__ == '__main__':
    create_csv()
