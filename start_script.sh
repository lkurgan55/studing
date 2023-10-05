#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip git -y

sudo git clone https://github.com/lkurgan55/studing.git
cd studing
sudo git checkout cloud_lab_2

sudo python3 -m pip install -r ./requirements.txt

export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=us-west-3

sudo crontab -l | { cat; sudo echo "@reboot python3 /studing/src/main.py"; } | crontab -
sudo python3 /studing/src/main.py &
