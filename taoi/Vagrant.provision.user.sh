# source the init script (this should use bash_completion to source automatically
# in subsequent logins
. /etc/bash_completion.d/virtualenvwrapper

mkvirtualenv -p /opt/jython/bin/jython jythonenv

cd /vagrant/external_dependencies

tar xzvf PyYAML-3.11.tar.gz

cd PyYAML-3.11

jython setup.py --without-libyaml install

# install requirements from pip requirements file
pip install -r /vagrant/requirements.txt

