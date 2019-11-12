#! /usr/bin/env python3

import logging
import logging.config
import os

from logging.handlers import TimedRotatingFileHandler
from time import localtime, strftime

import config


config = config.get_config()
archive_f = config['paths']['archive_dropfolder']
drop_f = config['paths']['mac_dropfolder']
divaname = config['paths']['DIVAName']

logger = logging.getLogger(__name__)


def set_logger():
    """Setup logging configuration
    """
    path = 'logging.yaml'

    with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
        logger = logging.config.dictConfig(config)

    return logger


def main(): 

    date_frmt = str(strftime('%A, %d. %B %Y %I:%M%p', localtime()))

    start_msg = f"\n\
    ================================================================\n \
                DIVA DMF Archive Script\n\
                Version: 0.0.1\n\
                Date: {date_frmt}\n\
    ================================================================\n\
    \n"

    logger.info(start_msg)
    logger.error(start_msg)


if __name__ == '__main__':
    set_logger()
    create_mdf()
