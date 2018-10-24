#! /usr/bin/env bash

# http://smirnov-am.blogspot.com/2015/04/installation-of-python-279-in-ubuntu.html
# http://davebehnke.com/python-pyenv-ubuntu.html
# https://renoirboulanger.com/blog/2015/04/upgrade-python-2-7-9-ubuntu-14-04-lts-making-deb-package/

# install dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
sudo apt-get install checkinstall

# download and extract python 2.7.9 source
mkdir ~/source
cd ~/source
wget http://python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar -xvf Python-2.7.9.tgz
sudo mv Python-2.7.9 python-current
#cd Python-2.7.9
cd python-current

# compile python source to new directory
sudo mkdir /opt/python-current
./configure --prefix=/opt/python-current
make

# use checkinstall to create and install deb package
sudo checkinstall --pkgname python-current

# display python version
/opt/python-current/bin/python -V

# install setuptools
curl https://bootstrap.pypa.io/ez_setup.py -o - | sudo /opt/python-current/bin/python

# use setuptools to install pip
sudo /opt/python-current/bin/easy_install -s /opt/python-current/bin -d /opt/python-current/lib/python2.7/site-packages/ pip

# update PATH to include the new version of python first
export PATH="/opt/python-current/bin:$PATH"

# package can then be removed with:
# sudo dpkg -r python-2.7.9