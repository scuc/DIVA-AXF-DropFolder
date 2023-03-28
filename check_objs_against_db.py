import json
import logging
import os
import shutil
import time

import api_DIVA as api
import config as cfg

config = cfg.get_config()

root_path = config["paths"]["script_root"]
mac_root_folders = config["paths"]["mac_root_path"]
archive_folders = [
    os.path.join(x, config["paths"]["archiving"]) for x in mac_root_folders
]
obj_category = config["DIVA_Obj_Category"]
source_dest = config["DIVA_Source_Dest"]

logger = logging.getLogger(__name__)


###############################################################################################
######  NOTE: This Script is set up to run as a stand alone procedure, operating on a    ######
######  serparate schedule from the main.py archiving script. the execution is schedule  ######
######  controlled by the launchd file: py.script.checkDivaObjects.plist                 ######
######  it runs 4x times a day, every 6 hours.                                           ######
################################################################################################


def get_archived_objects():
    """
    for each watch folder, create a list of directories present, check to see
    if the same directories are not already present in _archiving and
    _incomplete and a size larger than 0 KB.
    """
    duplicate_dict = {}
    unique_dict = {}
    index = 0
    for archivefolder in archive_folders:

        source_destination = source_dest[index]

        if source_destination == "Isilon2_Archive":
            volume_name = archivefolder[9:16]
        else:
            volume_name = archivefolder[9:17]

        check_df_msg = f"Checking archive folder on: {volume_name}"
        logger.info(check_df_msg)

        df_delimiter_msg = (
            f"\n\n=============== ARCHIVE FOLDER: {volume_name} ==================\n\n"
        )
        logger.info(df_delimiter_msg)
        print(df_delimiter_msg)

        dir_list = [
            d
            for d in os.listdir(archivefolder)
            if os.path.isdir(os.path.join(archivefolder, d))
        ]

        file_list = [
            f
            for f in os.listdir(archivefolder)
            if os.path.isfile(os.path.join(archivefolder, f))
            and f.endswith(".mov")
            or f.endswith(".mxf")
            or f.endswith(".xml")
        ]

        archive_list = dir_list + file_list

        if len(archive_list) == 0:
            empty_msg = f"{volume_name} = No objects in _archiving to check"
            print(empty_msg)
            logger.info(empty_msg)
            duplicate_dict.update({volume_name: []})
            unique_dict.update({volume_name: []})
            index += 1
            continue

        else:
            duplicate_list = []
            unique_list = []
            for objectName in archive_list:
                try:
                    status = api.file_check(objectName)
                    tapeInstances = api.get_object_info(objectName)
                    if status is True and tapeInstances == 1:
                        duplicate_list.append(objectName)
                        delete_obj(archivefolder, objectName)
                    else:
                        unique_list.append(objectName)
                except Exception as e:
                    logger.error(f"Exception on db check: \n{e}")

            duplicate_dict.update({volume_name: duplicate_list})
            unique_dict.update({volume_name: unique_list})

    t = time.time()
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    combined_dict = {
        "datestamp": date,
        "ARCHIVED": duplicate_dict,
        "UNARCHIVED": unique_dict,
    }
    # print(combined_dict)

    os.chdir(root_path)
    with open("_obj_check_log.json", "r") as f:
        data = json.load(f)
        f.close

        data["logs"].append(combined_dict)

    with open("_obj_check_log.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close


def delete_obj(archivefolder, objectName):

    path = os.path.join(archivefolder, objectName)
    isdir = os.path.isdir(path)
    isfile = os.path.isfile(path)

    print(objectName, isdir, isfile)

    if isdir is True:
        shutil.rmtree(path)
    elif isfile is True:
        os.remove(path)
    else:
        print(f"UNABLE TO DETERMINE OBJ TYPE- DIR or FILE")

    return


if __name__ == "__main__":
    get_archived_objects()
