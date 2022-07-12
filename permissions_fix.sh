#! /bin/bash

# /etc sudoers file edited to allow user 
# to run sudo command without password prompt

cd $1
sudo -u admin chflags nouchg ./

sudo find ./ -name '.?*' -prune -o -exec chmod 777 {} +
sudo find ./ -name '.?*' -prune -o -exec chmod -N {} +
sudo find ./ -name '.?*' -prune -o -exec chown 40006:50004 {} +
sudo find ./ -name '.?*' -prune -o -exec xattr -c {} +
