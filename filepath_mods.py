#! /usr/bin/env python3

import os
import re

from pathlib import Path


def check_pathname(path):
    """
    Check each path recursively, and elminiate any illegal characters.
    """

    for root, dirs, files in os.walk(path):

        for name in dirs: 
            pathname = os.path.join(root, name)
            print(f"     DIR NAME:   {pathname}")
            safe_pathname = makeSafeName(pathname)
            print(f"SAFE DIR NAME:   {safe_pathname}")
            print("")

        for name in files:
            pathname = os.path.join(root, name)
            print(f"     FILE NAME:  {pathname}")
            if pathname.endswith(".DS_Store"):
                os.remove(pathname)
                continue
            else:
                safe_pathname = makeSafeName(pathname)
                print(f"SAFE FILE NAME:   {safe_pathname}")
            print("-"*30)
    
    return 

def makeSafeName(pathname):
    """
    Check a path name against a list of illegal characters, remove any found. 
    """

    illegalchars = ["@", ":", "*", "?", '"', "'", "<", ">", "|", "&", "#", "%", "(", ")","$", "~", "+", "="]
    cleanpath = "".join([x for x in pathname if x not in illegalchars])
    
    if len(pathname) != len(cleanpath): 
        p = Path(pathname)
        cleanp = Path(cleanpath)
        p.rename(cleanp)
    else:
        cleanp = pathname 
    
    return cleanp


if __name__ == '__main__':
    check_pathname(path)



