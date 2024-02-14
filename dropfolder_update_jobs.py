
from datetime import datetime
import json
import os

import api_DIVA as api
import config as cfg

config = cfg.get_config()

root_path = config["paths"]["script_root"]


dedup_dlist = ['CesarMillansDogNation_UHJ107_FNGS_V749929_INT_C_EST_PROHQ1080p_23_PTX_178_ENG-51ST_RT004251_$TEMP$.mov', 'CritterFixersCountryVets_XXXXXX_ORIG_V30403853_INT_C_EST_PROHQ1080p_29_PTX_178_ENG-51ST_RT004404_$TEMP$.mov', 'Cesar911CesarToTheRescueAsia_UJV102_FNGS_V638804_INT_C_EST_PROHQ1080p_29_PTX_178_ENG-51ST_RT004109_$TEMP$.mov', 'CritterFixersCountryVets_XXXXXX_ORIG_V30403853_INT_C_EST_PROHQ1080p_29_ENG_178_ENG-51ST_RT004404_$TEMP$.mov', 'CesarMillansDogNation_UHJ106_FNGS_V749928_INT_C_EST_PROHQ1080p_23_PTX_178_ENG-51ST_RT004257_$TEMP$.mov', 'CritterFixersCountryVets_XXXXXX_ORIG_V30403853_INT_C_EST_PROHQ1080p_29_TEX_178_ENG-51ST_RT004404_$TEMP$.mov']

def update_dropfolder_json(dedup_dlist, volume_name):
    
    os.chdir(root_path)
    date = datetime.now()

    data_dict = {}

    with open("dropfolder_job_list.json", "w+") as f:

        for filename in dedup_dlist: 

            api_status = api.api_file_check(filename)

            data = f"""{{datetime: {date},filename: {filename},dropfolder: {volume_name},api_status: {api_status}}}"""

            data_dict.update(data)

            json_string = json.dumps(data_dict, indent=4)
            f.write(json_string)
        f.close

if __name__ == '__main__':
    update_dropfolder_json(dedup_dlist, volume_name="Quantum2")
