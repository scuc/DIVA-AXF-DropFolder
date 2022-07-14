import logging
import pprint

import pandas as pd
import requests
from pandas import json_normalize

import config as cfg
import get_authentication as auth

config = cfg.get_config()

url_core_manager = config["urls"]["core_manager_api"]
source_destinations = config["DIVA_Source_Dest"]

logger = logging.getLogger(__name__)


def file_check(objectName):
    """
    Use the DIVA REST API to check object against the DB to see if it already exists
    Status Code 200 = object found in DIVA DB
    Status Code 400 = invalid object name provided
    Status Code 404 = object not found in DIVA DB
    """

    try:
        token = auth.get_auth()
        # print(token)
        url_object_byobjectName = f"https://{url_core_manager}/objects/filesAndFolders"

        params = {
            "objectName": objectName,
            "collectionName": "AXF",
            "listType": 0,
            "startIndex": 1,
            "batchSize": 5,
        }

        headers = {
            "Accept": "application/json",
            "Authorization": token,
        }

        db_check_msg = f"Checking DIVA DB for object name:  {objectName}"
        logger.debug(db_check_msg)

        r = requests.get(
            url_object_byobjectName, headers=headers, params=params, verify=False
        )

        print("=" * 25)
        print(f"REQUEST URL: {r.request.url}")
        print(f"REQUEST BODY: {r.request.body}")
        print(f"REQUEST HEADERS: {r.request.headers}")
        print("=" * 25)

        response = r.json()

        code = r.status_code
        # print(f"============ {code} ==============")
        print("RESPONSE:")
        pprint.pprint(response)
        print(f"STATUS_CODE: {code}")

        status_code_msg = f"DIVA DB Check returned a status code: {code}"
        logger.debug(status_code_msg)

        if str(code) == "404":
            return False
        elif str(code) == "200":
            return True
        else:
            return "error"

    except Exception as e:
        api_exception_msg = f"Exception raised on the DIVA DB check: \n {e} \n"
        logger.error(api_exception_msg)
        return "error"


def get_requests(startDateTime):
    """
    Check DIVA to count the list of archive requests processed since 00:00:00 on the current day.
    The request is submitted with UTC time, and local server is eastern time, for the startDateTime
    is actually "05:00:00" to compensate.

    EXAMPLE FULL RESPONSE:
    {'id': 292865, 'abortReason': {'code': 0, 'description': '', 'name': 'DIVA_AR_NONE'
    }, 'additionalInfo': '<?xml version="1.0" encoding="UTF-8"?>\n<ADDITIONAL_INFO xmlns="http://www.fpdigital.com/divarchive/additionalInfoRequestInfo/v1.0"></ADDITIONAL_INFO>', 'completionDate': 1657682357, 'currentPriority': 66, 'destinationTape': '183375', 'objectName': 'NBLZ89604_LifeBelowZero_ShadowDwellers_2997p_AIR.mov', 'progress': 100, 'sourceTape': ' ', 'stateCode': 3, 'stateName': 'DIVA_COMPLETED', 'stateDescription': 'Completed', 'submissionDate': 1657681383, 'type': 'DIVA_ARCHIVE_REQUEST', 'typeDescription': 'Archive', 'typeCode': 0, 'statusCode': 1000, 'statusDescription': 'success', 'statusName': 'DIVA_OK', 'collectionName': 'AXF'
    }
    """
    try:
        token = auth.get_auth()
        url_requests = f"https://{url_core_manager}/requests"

        params = {
            "sortField": "ID",
            "sortDirection": "ASC",
            "type": "Archive",
            "startDateTime": {startDateTime},
            "states": [
                "Running",
                "Waiting for resources",
                "Waiting for operator",
                "Pending",
                "Transferring",
            ],
            "collectionName": "AXF",
        }

        headers = {
            "Accept": "application/json",
            "Authorization": token,
        }

        db_check_msg = f"Checking DIVA DB for archive requests"

        logger.info(db_check_msg)

        r = requests.get(url_requests, headers=headers, params=params, verify=False)
        response = r.json()
        # pprint.pprint(response)
        # print("")
        # print("")
        json_data = json_normalize(response)
        data = json_data["requests"][0]
        df = pd.DataFrame(
            data,
            columns=[
                "id",
                "objectName",
                "progress",
                "stateCode",
                "stateName",
                "stateDescription",
                "statusCode",
                "statusDescription",
            ],
        )
        return df

    except Exception as e:
        api_exception_msg = f"Exception raised on the DIVA DB check: \n {e} \n"
        logger.error(api_exception_msg)
        return "error"


if __name__ == "__main__":
    # file_check(objectName="84418-84425_068441-068448_Dailies_20200116_D19_AM_PM")
    get_requests(startDateTime="2022-07-14 00:00:00")
