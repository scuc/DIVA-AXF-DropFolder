#! /usr/bin/env python3

import os
import re

import config
import filepath_mods as fpmod


config = config.get_config()
df = config['paths']['mac_dropfolder']
divaname = config['paths']['DIVAName']


def create_mdf(): 
    """
    Check a watch folder for directory sets to archive. 
    Walk through each directory set and build a list
    of file/folder paths to archive. Use the path list
    to write a .mdf file that is used as the trigger for
    the DIVA archive job. 
    """

    dlist = [d for d in os.listdir(
        df) if os.path.isdir(os.path.join(df, d))]

    if len(dlist) != 0: 
        for d in dlist: 
            mdf_doc = d + '.mdf'
            if os.path.exists(os.path.join(df,mdf_doc)): 
                print("----------EXISTS------------")
                continue
            else: 
                pathslist = []
                dpath = os.path.join(df,d)
                fpath = fpmod.check_pathname(dpath)

                for root, dirs, files in os.walk(dpath): 
                    # for name in dirs:   
                    #     dpath = os.path.join(root, name)
                    #     dpath = dpath + "\\"
                    #     append_pathlist(dpath, pathslist)

                    for name in files: 
                        fpath = os.path.join(root,name)
                        if fpath.endswith('.DS_Store'):
                            os.remove(fpath)
                            print(f"REMOVING:    {fpath}")
                        else:
                            append_pathlist(fpath, pathslist)

                paths_string = '\n'.join(map(str, pathslist))
                print(paths_string)
                os.chdir(df)
                
                print("")
                print("*"*30)
                print("")

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
                                f"#sourceDestinationDIVAPath={df}\n"
                                f"\n"
                                f"<fileList>\n"
                                f"{paths_string}\n"
                                f"</fileList>"
                    )

                    mdf_doc.write(doc_body)
                    mdf_doc.close()


def append_pathlist(path, pathslist):
    """
    Build the list of files / folders and change any forward slashes to back slashes. 
    """

    bk_path = re.sub(r'/', r'\\', path)
    pathslist.append(bk_path[51:])

    return pathslist


if __name__ == '__main__':
    create_mdf()
