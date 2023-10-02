sudo dnf update
sudo dnf install python pip git -y

git clone https://github.com/lkurgan55/studing.git
cd studing
git checkout cloud_lab_1

sudo python -m pip install -r ./requirements.txt
sudo python main.py
