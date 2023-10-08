#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip git -y

sudo git clone -b cloud_lab_2 https://github.com/lkurgan55/studing.git

export AWS_ACCESS_KEY_ID=AKIAZGHC27RHI436XBBK
export AWS_SECRET_ACCESS_KEY=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

sudo python3 -m pip install -r ./studing/requirements.txt

sudo crontab -l | { cat; sudo echo "@reboot sudo -E python3 /studing/src/main.py"; } | crontab -
sudo -E python3 /studing/src/main.py &
