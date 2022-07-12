import logging
import pprint
import requests 

import config as cfg
import get_authentication as auth

config = cfg.get_config()

url_core_manager = config['urls']['core_manager_api']
source_destinations = config["DIVA_Source_Dest"]

logger = logging.getLogger(__name__)


def api_file_check(objectName):
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
                "listType":0,
                "startIndex":1,
                "batchSize":5,
                }

        headers = {
                "Accept": "application/json",
                "Authorization": token,
                }
        
        db_check_msg = f"Checking DIVA DB for object name:  {objectName}"
        logger.debug(db_check_msg)

        r = requests.get(url_object_byobjectName, headers=headers, params=params, verify=False)
        
        print("="*25)
        print(f"REQUEST URL: {r.request.url}")
        print(f"REQUEST BODY: {r.request.body}")
        print(f"REQUEST HEADERS: {r.request.headers}")
        print("="*25)

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
        api_exception_msg = f"EXCEPTION raised on the DIVA DB check: \n {e} \n"
        logger.error(api_exception_msg)
        return "error"


def api_archiving_check(): 
    """
    Check DIVA to count the number of active archive jobs.
    """


    


if __name__ == '__main__':
    api_file_check(objectName="84418-84425_068441-068448_Dailies_20200116_D19_AM_PM")