#! /bin/bash

cd /Volumes/Quantum3/__Archive/_AXF_Archive_DropFolder
sudo chflags -R nouchg ./
sudo chmod -R 777 ./
sudo chmod -RN ./
sudo chown -R admin:staff ./
sudo xattr -rc ./
