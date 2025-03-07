#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip git -y

sudo git clone -b cloud_lab_2 https://github.com/lkurgan55/studing.git

echo 'aws_access_key_id=' | sudo tee -a /studing/config.ini
echo 'aws_secret_access_key=' | sudo tee -a /studing/config.ini

sudo python3 -m pip install -r ./studing/requirements.txt

sudo crontab -l | { cat; sudo echo "@reboot sudo -E python3 /studing/src/main.py"; } | crontab -
sudo -E python3 /studing/src/main.py &
