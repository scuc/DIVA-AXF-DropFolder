#! /usr/bin/env python3

import logging
import os
import re

from pathlib import Path

logger = logging.getLogger(__name__)


def check_pathname(path):
    """
    Check each path recursively, and elminiate any illegal characters.
    """
    count = 0
    for root, dirs, files in os.walk(path):
        for name in dirs:
            pathname = os.path.join(root, name)
            safe_pathname = makeSafeName(pathname)

    for root, dirs, files in os.walk(path):
        for name in files:
            pathname = os.path.join(root, name)
            if pathname.endswith(".DS_Store"):
                os.remove(pathname)
                count += 1
                continue
            else:
                safe_pathname = makeSafeName(pathname)

    rm_msg = f"{count} .DS_Store files removed from dir before archive."
    logger.info(rm_msg)
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
        pathname_msg = f"\n\
        Illegal characters removed from pathname.\n\
        pathname:     {pathname} \n\
        safe pathname:     {cleanpath} \n "
        logger.info(pathname_msg)
    else:
        cleanp = pathname 
    
    return cleanp


if __name__ == '__main__':
    check_pathname(path)



