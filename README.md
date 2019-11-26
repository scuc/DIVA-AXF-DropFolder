# DIVA\_DMF\_DropFolder
A script for automating the creation of .MDF files that are used to trigger
DIVA Archive from withinb a DMF Drop folder. 

## Description
The script takes [DIVAArchive](https://www.goecodigital.com) to


The script follows a series of steps: 


1. Check the queue of folder sets in the archive location. <br> If the folder count is above the set threshold (default = 10), <br> pause the script for 5min and then check again. Continue this loop <br> until the archive queue is below the allowed count. <br>
<br>
2. Create a list of new folder sets in the DMF drop folder location. <br> If the length of the list is not zero, begin looping iterating the list of folder sets. <br>
<br>
3. For each fodler in the set list, check to the size to determine if the directory is still growing. <br> If the folder size is still growing after 90secs, move on the next directory on the list. <br>If it is not growing, move on to the next step. <br><br>
4. Walk the entire directory structure of each folder set, and <br> check each sub-directory and file name for illegal characters. <br> Replace or remove any that are found. <br><br>
5. Generate the .mdf trigger file each folder in the list that has passed the preceeding steps. <br><br>
6. Move the .mdf and its corresponding folder set into the archive location for DIVA to begin its archivng process. 

#### .mdf example: 

		#
		# Object configuration
		#
	
		priority=50
		objectName=81187_SeriesName_SMLS_GRFX
		categoryName=AXF
	
		<comments>
		81187_SeriesName_SMLS_GRFX
		</comments>
	
		#sourceDestinationDIVAName=[source-dest name defined in the DIVA Config Utility]
		#sourceDestinationDIVAPath=\\UNC path to\DIVA\DropFolder\Location\
	
		<fileList>
		81187_SeriesName_SMLS_GRFX/*
		</fileList>

**priority** = default priority for the archive job (0 - 100)<br>
**obejctName** = the name of the folder set. <br>
**categoryName** = the name of the DIVA tape Category, defined if the DIVA Config Utility<br>
**comments** = any comments relevant to the set, script defaults to the folder name.<br>
**sourceDestinationDIVAName** = the source-dest name defined in the DIVA Config Utility, not used in the .mdf<br>
**sourceDestinationDIVAPath** = the UNC path defined in the DIVA Config Utility, not used in the .mdf<br>
**fileList** = the files in the folder set the will be archived, defaults to the entire directory.<br>

**NOTE:** DIVAName and DIVAPath are not used in the .mdf because both of these values are constant and already defined in the Source-Destinations settings of the DIVA Config Utility.

## Prerequisites 

* Python 3.6 or higher
* [Diva Archive](https://www.goecodigital.com) 



## Files Included

* `main.py`
* `config.py`
* `dropfolder_check.py`
* `logging.yaml `
* `check_dir_size.py`
* `archive_queue.py`


## Getting Started

* Install prerequisities 
* Create a `config.yaml` document with the format: 
&nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; paths: &nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; mac\_archive\_folder:&nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; mac\_dropfolder:&nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; win\_dropfolder:&nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; win\_archive_folder:&nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; DIVAName:&nbsp;   &nbsp;   &nbsp;   &nbsp;   &nbsp;  
 

