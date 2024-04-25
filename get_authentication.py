import logging

import requests

import config as cfg

config = cfg.get_config()

creds_name = config["creds"]["name"]
creds_pw = config["creds"]["password"]
url_core_data = config["urls"]["core_data_api"]
url_core_manager = config["urls"]["core_manager_api"]

logger = logging.getLogger(__name__)


def get_auth():
    """
    POST request to users/login, returns auth token
    """
    try:
        url_user_login = f"https://{url_core_data}/users/login"

        json_payload = {"username": creds_name, "password": creds_pw}
        headers = {"Accept": "application/json"}
        response = requests.post(
            url_user_login, headers=headers, json=json_payload, verify=False
        )
        response.raise_for_status()
        token = response.json()["token"]

        return token

    except requests.exceptions.RequestException as e:
        auth_err_msg = f"Error authenticating with the DIVA API: \n{e}"
        logger.error(auth_err_msg)


if __name__ == "__main__":
    get_auth()
