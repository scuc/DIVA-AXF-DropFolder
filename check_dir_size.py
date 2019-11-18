#! /usr/bin/env python3

import logging
import os
import time

logger = logging.getLogger(__name__)


def check_dir_size(dpath):
    """
    Walk the dir of a potential archive and check to make sure the dir is not growing. 
    If so, wait 5 seconds and check again, if not return and create the .mdf file. 
    """
    checked_size = 0
    total_size = 0
    
    while True:
        print(f"TOTAL SIZE 01:   {total_size}")
        print(f"CHECKED SIZE 01:    {checked_size}" )
        try:     
            for dirpath, dirnames, filenames in os.walk(dpath):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    print(fp)
                    total_size += os.path.getsize(fp)
                    print(f"TOTAL SIZE 02:   {total_size}")
                    print(f"CHECKED SIZE 02:    {checked_size}" )
            print("BREAK")

            if total_size != checked_size:
                checked_size = total_size
                total_size = 0
                print(f"TOTAL SIZE 03:   {total_size}")
                print(f"CHECKED SIZE 03:    {checked_size}" )
                print("==========FOLDER IS STILL GROWING========")
                time.sleep(5)
                continue
            else:
                print(f"FOLDER NOT GROWING.")
                break
            break
        except Exception as e:
            print(e)
            break

    return total_size

print(check_dir_size())
