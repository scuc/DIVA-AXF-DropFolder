import os

import yaml


def get_config():
    """
    Setup configuration and credentials
    """
    path = "config.yaml"

    with open(path, "rt") as f:
        config = yaml.safe_load(f)

    return config


def ensure_dirs():
    dirs = ["_logs"]

    for dir in dirs:
        os.makedirs(dir, exist_ok=True)

    return


if __name__ == "__main__":
    get_config()
