#!/usr/bin/env bash

sudo apt-get update

# install pip if it doesn't exist yet
which pip > /dev/null 2>&1
if [ $? -ne 0 ]; then
    sudo apt-get install -q -y python-pip
fi

# install python development headers
dpkg --get-selections | grep python-dev > /dev/null 2>&1
if [ $? -ne 0 ]; then
    sudo apt-get install -q -y python-dev
fi

# install virtualenvwrapper (if you're using bash, otherwise install virtualenv
# and figure out how to use it with your stupid shell of choice)
sudo apt-get install -q -y python-virtualenv
sudo apt-get install -q -y virtualenvwrapper

# source the init script (this should use bash_completion to source automatically
# in subsequent logins
. /etc/bash_completion.d/virtualenvwrapper

# install requirements from pip requirements file
sudo pip install -r /vagrant/requirements.txt


wget http://search.maven.org/remotecontent?filepath=org/python/jython-installer/2.7-b4/jython-installer-2.7-b4.jar -O jython_installer.jar

