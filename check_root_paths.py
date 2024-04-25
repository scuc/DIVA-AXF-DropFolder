import logging
import logging.config
import os

import config

config = config.get_config()

script_root = config["paths"]["script_root"]
mac_root_folders = config["paths"]["mac_root_path"]
drop_folders = [
    os.path.join(x, config["paths"]["drop_folder"]) for x in mac_root_folders
]

logger = logging.getLogger(__name__)


def check_root_paths():
    root_folders = []

    for volume in mac_root_folders:
        volume_present = os.path.ismount(volume)
        root_folders.append([volume, volume_present])

    for location in root_folders:
        if not location[1]:
            mount_err_msg = f"Volume is missing: {location[0]}"
            logger.error(mount_err_msg)
            return False

    return True


if __name__ == "__main__":
    check_root_paths()
