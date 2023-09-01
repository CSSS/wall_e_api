# wall_e_website


 - [1. Setup Python Environment](#1-setup-python-environment)
 - [2. Setup and Run Website](#2-setup-and-run-website)
 - [3. Before opening a PR](#3-before-opening-a-pr)
 - [Various tasks to accomplish](#various-tasks-to-accomplish)


## 1. Setup Python Environment
### for Debian based OS
```shell
sudo apt-get install -y python3.9
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.7 get-pip.py --user
python3.7 -m pip install virtualenv --user
python3.7 -m virtualenv wall_e_website
. wall_e_website/bin/activate
```

### for MacOS
open to anyone to make a PR adding this section

### for Windows
open to anyone to make a PR adding this section

## 2. Setup and Run Website
```
If you hve not cloned your forked version yet
wget https://raw.githubusercontent.com/CSSS/wall_e_website/master/download_repo.sh
./download_repo.sh

If you have forked your version
./run_site.sh
```

### 2.1 To make any needed changes to the models
```shell
python -m pip uninstall wall_e_models

https://github.com/CSSS/wall_e_models.git
cd wall_e_models
# make any necessary changes

# package model
python3 setup.py sdist

# install package for wall_e
python -m pip install ../wall_e_models/dist/wall_e_models-0.X.tar.gz
```