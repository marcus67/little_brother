#! /bin/bash

#    Copyright (C) 2019  Marcus Rickert
#
#    See https://github.com/marcus67/python_base_app
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

##################################################################################
# Please, beware that this file has been generated! Do not make any changes here #
# but only to python_base_app/templates/debian_postinst.template.sh!             #
##################################################################################


TMP_DIR=/tmp
ETC_DIR=/etc/little-brother
LOG_DIR=/var/log/little-brother
SPOOL_DIR=/var/spool/little-brother
LIB_DIR=/var/lib/little-brother
VIRTUAL_ENV_DIR=/var/lib/little-brother/virtualenv
SYSTEMD_DIR=/lib/systemd/system
TMPFILE_DIR=/usr/lib/tmpfiles.d
SUDOERS_DIR=/etc/sudoers.d
APPARMOR_DIR=/etc/apparmor.d


ROOT_DIR=
SCRIPT_DIR=$(dirname ${BASH_SOURCE[0]})
INSTALL_BASE_DIR=$(realpath $SCRIPT_DIR/..)
echo "Running generic installation script with base directory located in $INSTALL_BASE_DIR..."

if [ ! "$EUID" == "0" ] ; then
    echo "ERROR: You have to be root to call this script."
    exit 2
fi

echo "Checking if all Pip packages have been downloaded to $TMP_DIR..."
if [ ! -f $TMP_DIR/little-brother-0.3.13.tar.gz ] ; then
  echo "ERROR: package little-brother-0.3.13.tar.gz not found in $TMP_DIR!"
  echo "Download from test.pypi.org and execute again."
  exit 2
else
  echo "Package little-brother-0.3.13.tar.gz was found."
fi

if [ ! -f $TMP_DIR/python-base-app-0.2.16.tar.gz ] ; then
  echo "ERROR: package python-base-app-0.2.16.tar.gz not found in $TMP_DIR!"
  echo "Download from test.pypi.org and execute again."
  exit 2
else
  echo "Package python-base-app-0.2.16.tar.gz was found."
fi

if [ ! -f $TMP_DIR/some-flask-helpers-0.2.2.tar.gz ] ; then
  echo "ERROR: package some-flask-helpers-0.2.2.tar.gz not found in $TMP_DIR!"
  echo "Download from test.pypi.org and execute again."
  exit 2
else
  echo "Package some-flask-helpers-0.2.2.tar.gz was found."
fi

mkdir -p ${SYSTEMD_DIR}
cp ${INSTALL_BASE_DIR}/etc/little-brother.service ${SYSTEMD_DIR}/little-brother.service
mkdir -p ${SUDOERS_DIR}
cp ${INSTALL_BASE_DIR}/etc/little-brother.sudo ${SUDOERS_DIR}/little-brother
mkdir -p ${APPARMOR_DIR}
cp ${INSTALL_BASE_DIR}/etc/little-brother.apparmor ${APPARMOR_DIR}/little-brother.conf
TARGET_DIRECTORY=${ROOT_DIR}/$(dirname etc/little-brother/slave.config )
mkdir -p ${TARGET_DIRECTORY}
echo "Deploying extra file '$INSTALL_BASE_DIR/etc/slave.config' to '${ROOT_DIR}/etc/little-brother/slave.config'..."
cp -f $INSTALL_BASE_DIR/etc/slave.config ${ROOT_DIR}/etc/little-brother/slave.config
TARGET_DIRECTORY=${ROOT_DIR}/$(dirname etc/little-brother/master.config )
mkdir -p ${TARGET_DIRECTORY}
echo "Deploying extra file '$INSTALL_BASE_DIR/etc/master.config' to '${ROOT_DIR}/etc/little-brother/master.config'..."
cp -f $INSTALL_BASE_DIR/etc/master.config ${ROOT_DIR}/etc/little-brother/master.config



if grep -q 'little-brother:' /etc/group ; then
    echo "Group 'little-brother' already exists. Skipping group creation."
else
    #echo "Adding group 'little-brother'..."
    if [ "${APP_GID}" == "" ] ; then
        groupadd little-brother
    else
	      groupadd --gid ${APP_GID} little-brother
    fi
fi
if grep -q 'little-brother:' /etc/passwd ; then
    echo "User 'little-brother' already exists. Skipping user creation."
else
    if  [ "${APP_UID}" == "" ] ; then
#        adduser --gid little-brother --gecos "" --no-create-home --disabled-password little-brother
        useradd --gid little-brother --no-create-home little-brother
    else
#        adduser --gid little-brother --uid ${APP_UID} --gecos "" --no-create-home --disabled-password little-brother
        useradd --gid little-brother --uid ${APP_UID} --no-create-home little-brother
    fi
fi

set -e
usermod -aG audio little-brother


echo "Creating directories..."
echo "    * ${LOG_DIR}"
mkdir -p ${LOG_DIR}
echo "    * ${SPOOL_DIR}"
mkdir -p ${SPOOL_DIR}
echo "    * ${LIB_DIR}"
mkdir -p ${LIB_DIR}


if [ -f /etc/little-brother/little-brother.config ] ; then
  echo "Template '/etc/little-brother/master.config' already exists as '/etc/little-brother/little-brother.config' -> SKIPPING"
else
  echo "Deploying template file '/etc/little-brother/master.config' to '/etc/little-brother/little-brother.config'..."
  cp -f /etc/little-brother/master.config /etc/little-brother/little-brother.config
fi


echo "Creating symbolic link /usr/local/bin/run_little_brother.py --> ${VIRTUAL_ENV_DIR}/bin/run_little_brother.py..."
ln -fs ${VIRTUAL_ENV_DIR}/bin/run_little_brother.py /usr/local/bin/run_little_brother.py
echo "Creating symbolic link /usr/local/bin/run_little_brother_test_suite.py --> ${VIRTUAL_ENV_DIR}/bin/run_little_brother_test_suite.py..."
ln -fs ${VIRTUAL_ENV_DIR}/bin/run_little_brother_test_suite.py /usr/local/bin/run_little_brother_test_suite.py

echo "Creating virtual Python environment in ${VIRTUAL_ENV_DIR}..."

virtualenv -p /usr/bin/python3 ${VIRTUAL_ENV_DIR}

PIP3=${VIRTUAL_ENV_DIR}/bin/pip3

echo "Setting ownership..."
echo "    * little-brother.little-brother ${ETC_DIR}"
chown -R little-brother.little-brother ${ETC_DIR}
echo "    * little-brother.little-brother ${LOG_DIR}"
chown -R little-brother.little-brother ${LOG_DIR}
echo "    * little-brother.little-brother ${SPOOL_DIR}"
chown -R little-brother.little-brother ${SPOOL_DIR}
echo "    * little-brother.little-brother ${LIB_DIR}"
chown -R little-brother.little-brother ${LIB_DIR}


echo "    * little-brother.little-brother /etc/little-brother/little-brother.config"
chown little-brother.little-brother /etc/little-brother/little-brother.config
echo "    * ${SYSTEMD_DIR}/little-brother.service"
chown root.root ${SYSTEMD_DIR}/little-brother.service

echo "    * ${SUDOERS_DIR}"
chown root.root ${SUDOERS_DIR}
echo "    * ${SUDOERS_DIR}/little-brother"
chown root.root ${SUDOERS_DIR}/little-brother

echo "    * ${APPARMOR_DIR}/little-brother.conf"
chown root.root ${APPARMOR_DIR}/little-brother.conf


echo "Setting permissions..."
echo "    * ${ETC_DIR}"
chmod -R og-rwx ${ETC_DIR}
echo "    * ${LOG_DIR}"
chmod -R og-rwx ${LOG_DIR}
echo "    * ${SPOOL_DIR}"
chmod -R og-rwx ${SPOOL_DIR}


echo "    * little-brother.little-brother /etc/little-brother/little-brother.config"
chmod og-rwx /etc/little-brother/little-brother.config

${PIP3} --version
${PIP3} install wheel setuptools
echo "Installing PIP packages..."
echo "  * little-brother-0.3.13.tar.gz"
echo "  * python-base-app-0.2.16.tar.gz"
echo "  * some-flask-helpers-0.2.2.tar.gz"
# see https://stackoverflow.com/questions/19548957/can-i-force-pip-to-reinstall-the-current-version
${PIP3} install --upgrade --force-reinstall \
     ${TMP_DIR}/little-brother-0.3.13.tar.gz\
     ${TMP_DIR}/python-base-app-0.2.16.tar.gz\
     ${TMP_DIR}/some-flask-helpers-0.2.2.tar.gz


echo "Removing installation file ${TMP_DIR}/little-brother-0.3.13.tar.gz..."
rm ${TMP_DIR}/little-brother-0.3.13.tar.gz
echo "Removing installation file ${TMP_DIR}/python-base-app-0.2.16.tar.gz..."
rm ${TMP_DIR}/python-base-app-0.2.16.tar.gz
echo "Removing installation file ${TMP_DIR}/some-flask-helpers-0.2.2.tar.gz..."
rm ${TMP_DIR}/some-flask-helpers-0.2.2.tar.gz