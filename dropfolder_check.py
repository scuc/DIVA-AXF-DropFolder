#! /usr/bin/env python3

import logging
import os
import re
import shutil

import config
import archive_queue as aqueue
import check_dir_size as checksize
import filepath_mods as fpmod


config = config.get_config()
archive_f = config['paths']['mac_archive_folder']
drop_f = config['paths']['mac_dropfolder']
divaname = config['paths']['DIVAName']

logger = logging.getLogger(__name__)


def create_mdf(): 
    """
    Check a watch folder for directory sets to archive. 
    Walk through each directory set and build a list
    of file/folder paths to archive. Use the path list
    to write a .mdf file that is used as the trigger for
    the DIVA archive job. 
    """

    queue_status = aqueue.archiving_check()

    if queue_status != 0:
        return
    else:
        pass

    dlist = [d for d in os.listdir(
        drop_f) if os.path.isdir(os.path.join(drop_f, d)) and 
        d != "_archiving"]

    if dlist == []:
        empty_msg = f"No new dir for DMF archiving."
        logger.info(empty_msg)
        return
    else: 
        dlist_msg = f"New directories for DMF archiving: {dlist}"
        logger.info(dlist_msg)

    if len(dlist) != 0: 
        count = 0
        for d in dlist: 
            movelist = []
            mdf_doc = d + '.mdf'
            if os.path.exists(os.path.join(archive_f,mdf_doc)):
                dlist.remove(d)
                fileexist_msg = f"{mdf_doc} already exists in the archive folder, skipping"
                logger.info(fileexist_msg)
                continue
            elif count > 5: 
                max_count_msg = f"Maximum number of folder submissions reached for this archive cycle."
                logger.info(max_count_msg)
                return
            else: 
                dpath = os.path.join(drop_f,d)
                dir_value = checksize.check_dir_size(dpath)
                if dir_value == 1:
                    continue
                else:
                    fpath = fpmod.check_pathname(dpath)

                    paths_string = f"{d}/*"

                    os.chdir(drop_f)

                    with open(mdf_doc, mode="w", encoding='utf-8-sig') as mdf_doc:

                        doc_body = (
                                    f"#\n"
                                    f"# Object configuration.\n"
                                    f"#\n"
                                    f"\n"
                                    f"priority=50\n"
                                    f"objectName={d}\n"
                                    f"categoryName=AXF\n"
                                    f"\n"
                                    f"<comments>\n"
                                    f"{d}\n"
                                    f"</comments>\n"
                                    f"\n"
                                    f"#sourceDestinationDIVAName={divaname}\n"
                                    f"#sourceDestinationDIVAPath={drop_f}\n"
                                    f"\n"
                                    f"<fileList>\n"
                                    f"{paths_string}\n"
                                    f"</fileList>"
                                    )

                        mdf_doc.write(doc_body)
                        mdf_doc.close()
                        movelist.extend([dpath, os.path.join(drop_f, d + ".mdf")])
                        new_mdf_msg = f"New .mdf file created: {d + '.mdf'}"
                        logger.info(new_mdf_msg)

                    moved_list = move_to_checkin(movelist)
                    move_msg = f"The following directories have been moved into the archiving location: \n{moved_list}"
                    logger.info(move_msg)
                    count+=1 
    else:
        return


def move_to_checkin(movelist):
    """
    Move files and dir in the movelist from the drop folder to the archive location.
    """
    moved_list = []
    for x in movelist:
        arch_check = os.path.basename(x)
        try:
            if os.path.exists(os.path.join(archive_f, arch_check)): 
                print(f"{arch_check} already exists in this location, skipping")
                pass
            else:
                shutil.move(x, archive_f)
                if x.endswith(".mdf"):
                    pass
                else:
                    moved_list.append(arch_check)
        except Exception as e:
            move_excp_msg = f"\n\
            Exception raised on moving {x}.\n\
            Error Message:  {str(e)} \n\
            "
            logger.error(move_excp_msg)

    return moved_list


if __name__ == '__main__':
    create_mdf()
