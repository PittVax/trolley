#!/usr/bin/env bash

#PROVISIONED="/root/PROVISIONED";
#
#if [[ -f $PROVISIONED ]]; then
#  echo "Skipping provisioning";
#  exit;
#else
#  echo "Provisioning";
#fi


echo "192.168.123.1 treeage_host" >> /etc/hosts

apt-get update

# install pip if it doesn't exist yet
which pip > /dev/null 2>&1
if [ $? -ne 0 ]; then
    apt-get install -q -y python-pip
fi

# install python development headers
dpkg --get-selections | grep python-dev > /dev/null 2>&1
if [ $? -ne 0 ]; then
    apt-get install -q -y python-dev
fi

# install virtualenvwrapper (if you're using bash, otherwise install virtualenv
# and figure out how to use it with your stupid shell of choice)
apt-get install -q -y python-virtualenv
apt-get install -q -y virtualenvwrapper

apt-get install -q -y openjdk-7-jre

wget http://search.maven.org/remotecontent?filepath=org/python/jython-installer/2.7-b4/jython-installer-2.7-b4.jar -O /opt/jython_installer.jar

java -jar /opt/jython_installer.jar -s -d /opt/jython

chown -R vagrant /opt/jython

# become the vagrant user for remainder of provisioning
su -c "source /vagrant/Vagrant.provision.user.sh" vagrant

# indicate that provisioning has already occurred
#touch $PROVISIONED;



