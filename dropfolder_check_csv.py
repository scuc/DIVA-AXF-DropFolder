#! /usr/bin/env python3
import csv
import glob
import logging
import os
import shutil
import time
from pathlib import Path

import api_DIVA as api
import archive_queue as aqueue
import check_obj_size as checksize
import config
import filepath_mods as fpmod

config = config.get_config()

script_root = config["paths"]["script_root"]
mac_root_folders = config["paths"]["mac_root_path"]
csv_archive_dropfolder = config["paths"]["csv_dropfolder"]
drop_folders = [
    os.path.join(x, config["paths"]["drop_folder"]) for x in mac_root_folders
]
archive_error_f = [os.path.join(x, config["paths"]["error"]) for x in mac_root_folders]
archive_folders = [
    os.path.join(x, config["paths"]["archiving"]) for x in mac_root_folders
]
# diva servers are Win, use UNC to view files.
archive_f_win = config["paths"]["win_archive"]
duplicate_object_dir = config["paths"]["duplicates"]

obj_category = config["DIVA_Obj_Category"]
source_dest = config["DIVA_Source_Dest"]


logger = logging.getLogger(__name__)


def create_csv():
    """
    Check a watch folder for directory sets to archive.
    Walk through each directory set and build a list
    of file/folder paths to archive. Use the path list
    to write a .csv file that is used as the trigger for
    the DIVA archive job.
    """

    # for f in drop_folders: 
    #     csv_count = get_csv_count(f)
    #     counter = 0
    #     while csv_count != 0 and counter < 1:
    #         csv_msg = f"Counter:{counter}, CSV file still present in {f}, pausing script for 60sec."
    #         logger.info(csv_msg)
    #         time.sleep(60)
    #         counter += 1
    #         csv_count = get_csv_count(f)

    #         if csv_count != 0 and counter == 5:
    #             csv_msg = f"Counter:{counter}, CSV file still present in {f} after 5min, removing existing CSV."
    #             logger.info(csv_msg)
    #             csv_cleanup(f)
    #         else:
    #             continue

    queue_status = aqueue.archiving_check()

    if queue_status != 0:
        return
    else:
        pass

    """
    for each watch folder, create a list of directories present, check to see
    if the same directories are not already present in _archiving and
    _incomplete and a size larger than 0 KB.
    """
    index = 0
    submission_count = 0
    t = time.time()
    date = time.strftime("%Y%m%d%H%M", time.localtime(t))
    csv_doc = f"{date}_divaview.csv"

    for dropfolder in drop_folders:

        source_destination = source_dest[index]

        if source_destination == "Isilon2_Archive":
            volume_name = dropfolder[9:16]
        elif source_destination == "NG-Editorial_Archive": 
            volume_name = dropfolder[9:21] 
        else:
            volume_name = dropfolder[9:17]

        comments = volume_name

        check_df_msg = f"Checking drop folder on: {volume_name}"
        logger.info(check_df_msg)

        archive_f_windows = archive_f_win[index]

        df_delimiter_msg = f"\n\n====================== DROP FOLDER: {volume_name} =========================\n\n"
        logger.info(df_delimiter_msg)

        dir_list = [
            d
            for d in os.listdir(dropfolder)
            if os.path.isdir(os.path.join(dropfolder, d))
            and d not in ["_archiving", "_incomplete"]
        ]

        file_list = [
            f
            for f in os.listdir(dropfolder)
            if os.path.isfile(os.path.join(dropfolder, f))
            and f not in ["_archiving", "_incomplete"]
            and not f.startswith(".")
            and f.endswith(".mov")
            or f.endswith(".mxf")
            or f.endswith(".xml")
            or f.endswith(".tar")
            or f.endswith(".zip")
        ]

        archive_list = dir_list + file_list
        print(f"ARCHIVE LIST: {archive_list}")

        if len(archive_list) == 0:
            empty_msg = f"{volume_name} = No new dir for archiving."
            logger.info(empty_msg)
            index += 1
            continue

        else:
            try: 
                archive_list_size_checked = []
                for x in archive_list:
                    dpath = os.path.join(dropfolder, x)
                    if source_destination not in ["Isilon2_Archive", "NG-Editorial"]:  #size check does not work on Isilon2
                        total_size = checksize.get_object_size(dpath)
                        if total_size == 0: 
                            logger.info(f"Total filesize for {x} measured as 0. Removing from archive_list.")
                            continue
                        else:
                            archive_list_size_checked.append(x)
                    else: 
                        archive_list_size_checked.append(x)

            except Exception as e: 
                logger.error(f"Exception raised on total size check: \n{e}")


            archive_list = archive_list_size_checked[:10]  # only take 10 at a time,
            # avoid scenario when 1000's of dir dropped

            dedup_dlist = dedup_list(archive_list, date, dropfolder, index)

            dlist_msg = f"New directories for archiving: {dedup_dlist}"
            logger.info(dlist_msg)

            movelist = []
            # movelist.append(os.path.join(dropfolder, csv_doc))

            csv_tmp = os.path.join(script_root, "_csv_tmp")
            os.chdir(csv_tmp)

            with open(f"{csv_doc}", mode="a", newline="", encoding="utf-8-sig") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",")

                for d in dedup_dlist:
                    dpath = os.path.join(dropfolder, d)
                    dir_value = checksize.check_obj_size(dpath)

                    if dir_value == 0 or dir_value == 1:
                        continue

                    elif dir_value == 3:
                        oserror_msg = f"OSError found, likely illegal characters, unable to correct, moving to ERROR folder."
                        logger.error(oserror_msg)
                        shutil.move(
                            dpath,
                        )

                    else:
                        validation_result = fpmod.check_pathname(dpath)

                        if validation_result == 1: 
                            continue

                        if submission_count == 0:
                            csv_writer.writerow(
                                [
                                    "object name",
                                    "object category",
                                    "source destination",
                                    "root path",
                                    "list of files",
                                    "comments",
                                ]
                            )

                        if submission_count == 20:
                            max_count_msg = f"Maximum number of submissions reached for this archive cycle."
                            logger.info(max_count_msg)
                            break

                        if os.path.isfile(dpath):
                            csv_writer.writerow(
                                [
                                    f"{d}",
                                    obj_category,
                                    source_destination,
                                    archive_f_windows,
                                    f"{d}",
                                    comments,
                                ]
                            )
                        else:
                            csv_writer.writerow(
                                [
                                    f"{d}",
                                    obj_category,
                                    source_destination,
                                    archive_f_windows,
                                    f"{d}/*",
                                    comments,
                                ]
                            )

                        movelist.append(dpath)

                    submission_count += 1

                csv_file.close()

                new_csv_msg = f".csv file updated for {volume_name}"
                logger.info(new_csv_msg)

                moved_list = move_to_checkin(movelist, dropfolder)
                move_msg = (
                    f"Directories moved into archiving on {volume_name}: \n{moved_list}"
                )
                logger.info(move_msg)
                
                shutil.move(os.path.join(csv_tmp, csv_doc), csv_archive_dropfolder)
                logger.info(f"csv file moved from tmp to the watch folder: {csv_doc}")

        index += 1
    



def get_csv_count(f):
    """
    Get the count of CSV files in the specified directory.

    Args:
        f (str): The directory path.

    Returns:
        int: The count of CSV files in the directory.
    """
    os.chdir(f)
    csv_watchf = glob.glob("*.csv", recursive=False)

    os.chdir(os.path.join(f,"_archiving"))
    csv_archivingf = glob.glob("*.csv", recursive=False)

    csv_count = len(csv_watchf) + len(csv_archivingf)
    logger.info(f"CSV count for {f.split('/')[2]} is {csv_count}.")

    return csv_count


def csv_cleanup(drop_f):
    """
    Remove all CSV files from the drop folder and the _archiving folder.

    Args:
        drop_f (str): The path to the drop folder.

    Raises:
        OSError: If there is an error removing the CSV files.

    Returns:
        None
    """
    try:
        dropf_path = Path(drop_f).glob("*.csv")
        archiving_path = Path(drop_f, "_archiving").glob("*.csv")
        csv_paths = dropf_path + archiving_path

        for f in csv_paths:
            f.unlink()
            csv_del_msg = f"csv deleted from drop folder: {f}"
            logger.info(csv_del_msg)

        return

    except OSError as e:
        unlink_error_msg = (
            f"Error Removeing old .CSV: {f}: {e.strerror}"
        )
        logger.error(unlink_error_msg)


def dedup_list(archive_list, date, dropfolder, index):
    """
    check list of directories against the DIVA DB, look for duplicates and remove from list
    """
    dedup_dlist = []
    duplicates = []
    for d in archive_list:
        try:
            archive_object = os.path.join(dropfolder, d)
            duplicate = api.file_check(d)

            if duplicate == True:
                duplicates.append(d)

            elif duplicate == "error":
                dup_err_msg = (
                    f"Error returned on duplicate check, moving to Archive Error: {d}"
                )
                logger.error(dup_err_msg)
                shutil.move(archive_object, archive_error_f[index])
            else:
                dedup_dlist.append(d)
        except Exception as e:
            dup_excp_msg = f"Exception raised on Duplicate check: \n {e}"
            logger.error(dup_excp_msg)

    dedup_dlist_msg = f"New archive list after duplicates removed: {dedup_dlist}"
    logger.info(dedup_dlist_msg)

    duplicates_msg = f"Duplicates detected: {duplicates}"
    logger.info(duplicates_msg)

    renamed_obj_list = dup_rename(duplicates, date, dropfolder)

    # for arch_obj_dt in renamed_obj_list:
    #     shutil.move(
    #         os.path.join(dropfolder, arch_obj_dt),
    #         os.path.join(mac_root_folders[index], duplicate_object_dir, arch_obj_dt),
    #     )
    #     obj_mv_msg = f"Duplicate object, moved out of dropfolder:  {arch_obj_dt}"
    #     logger.info(obj_mv_msg)

    return dedup_dlist


def dup_rename(duplicates, date, dropfolder):
    """
    Renames duplicate objects in the dropfolder with a datetime stamp.

    Args:
        duplicates (list): A list of duplicate object names.
        date (str): The current date in the format 'YYYY-MM-DD'.
        dropfolder (str): The path to the dropfolder directory.

    Returns:
        list: A list of renamed object names.

    Raises:
        Exception: If an error occurs during the renaming process.

    """
    renamed_obj_list = []
    try:
        for dup in duplicates:
            archive_object = os.path.join(dropfolder, dup)
            if os.path.isdir(archive_object):
                arch_obj_dt = f"{archive_object}_{date}"
            else:
                arch_obj_dt = f"{archive_object[:-4]}_{date}{archive_object[-4:]}"

            if arch_obj_dt is None:
                continue
            else:
                os.rename(archive_object, arch_obj_dt)
                obj_rename_msg = f"Duplicate object, renamed:  {arch_obj_dt}"
                logger.info(obj_rename_msg)

            renamed_obj_list.append(os.path.basename(arch_obj_dt))

        return renamed_obj_list

    except Exception as e:
        rename_excp_msg = f"\n\
        Exception raised on dup rename {dup}.\n\
        Error Message:  {str(e)} \n\
        "
        logger.error(rename_excp_msg)

    return


def move_to_checkin(movelist, dropfolder):
    """
    Moves files from the movelist to the check-in location in the dropfolder.

    Args:
        movelist (list): A list of file paths to be moved.
        dropfolder (str): The path to the dropfolder.

    Returns:
        list: A list of file names that were successfully moved.

    Raises:
        Exception: If an error occurs while moving a file.

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
                shutil.move(x, os.path.join(dropfolder, "_archiving"))
                moved_list.append(proj_folder)
        except Exception as e:
            move_excp_msg = f"\n\
            Exception raised on moving {x}.\n\
            Error Message:  {str(e)} \n\
            "
            logger.error(move_excp_msg)

    return moved_list


if __name__ == "__main__":
    get_csv_count()
