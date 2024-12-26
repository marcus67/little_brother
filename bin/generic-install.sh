#! /bin/bash

#    Copyright (C) 2019-2024  Marcus Rickert
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

##################################################################################
# PARAMETERS                                                                     #
##################################################################################
# When set, will deactivate portions that are not applicable to Docker containers
RUNNING_IN_DOCKER=${RUNNING_IN_DOCKER:-}

# When set, contains an extra PIP index to download from
# This will be required when trying to install the version of the `master` branch since the required PIP packages
# may not be available ot pypi.org yet. In this case, add the extra index https://test.pypi.org/simple/
TEST_PYPI_EXTRA_INDEX=${TEST_PYPI_EXTRA_INDEX:-}

# When set, will create the application user with a specific user id
APP_UID=${APP_UID:-}

# When set, will create the application group with a specific group id
APP_GID=${APP_UID:-}

##################################################################################

if [ -f /etc/os-release ] ; then
  . /etc/os-release
else
  echo "Cannot read /etc/os-release!"
  exit 2
fi

echo "Detected operating system architecture '${ID}'."

function add_group() {
  group_name=$1
  group_id=$2

  if [ "$ID" == "alpine" ] ; then
    if [ "${group_id}" == "" ] ; then
      addgroup ${group_name}
    else
      addgroup -g ${group_id} ${group_name}
    fi
  else
    if [ "${group_id}" == "" ] ; then
      groupadd little_brother
    else
      groupadd --gid ${group_id} ${group_name}
    fi

  fi
}

function add_user() {
  user_name=$1
  group_name=$2
  user_id=$3

  if [ "$ID" == "alpine" ] ; then
    if  [ "${user_id}" == "" ] ; then
        adduser -G ${group_name} -g "" -H -D ${user_name}
    else
        adduser -G ${group_name} -u ${user_id} -g "" -H -D ${user_name}
    fi
  else
    if  [ "${user_id}" == "" ] ; then
        useradd --gid ${group_name} --no-create-home ${user_name}
    else
        useradd --gid ${group_name} --uid ${user_id} --no-create-home ${user_name}
    fi
  fi

}

function add_user_to_group() {
  user_name=$1
  group_name=$2

  if [ "$ID" == "alpine" ] ; then
    adduser ${user_name} ${group_name}
  else
    usermod -aG ${group_name} ${user_name}
  fi
}

export VIRTUAL_ENV_DIR=/var/lib/little_brother/virtualenv

ETC_DIR=/etc/little_brother
LOG_DIR=/var/log/little_brother
SPOOL_DIR=/var/spool/little_brother
LIB_DIR=/var/lib/little_brother
SYSTEMD_DIR=/lib/systemd/system
TMPFILE_DIR=/usr/lib/tmpfiles.d
SUDOERS_DIR=/etc/sudoers.d
APPARMOR_DIR=/etc/apparmor.d

ROOT_DIR=
SCRIPT_DIR=$(dirname ${BASH_SOURCE[0]})
INSTALL_BASE_DIR=$(realpath $SCRIPT_DIR/..)
BIN_DIR=${INSTALL_BASE_DIR}/bin



echo "Creating lib directories..."
echo "    * ${LIB_DIR}"
mkdir -p ${LIB_DIR}

echo "Running generic installation script with base directory located in $INSTALL_BASE_DIR..."

if [ ! "$EUID" == "0" ] ; then
    echo "ERROR: You have to be root to call this script."
    exit 2
fi

PIP3=${SCRIPT_DIR}/pip3.sh
chmod +x ${PIP3}
echo "Downloading Pip packages to $LIB_DIR..."
${PIP3} download -d $LIB_DIR --no-deps little_brother==0.5.2

${PIP3} download -d $LIB_DIR --no-deps python_base_app==0.3.1

${PIP3} download -d $LIB_DIR --no-deps some_flask_helpers==0.2.8


echo "Checking if all Pip packages have been downloaded to $LIB_DIR..."
if [ ! -f $LIB_DIR/little_brother-0.5.2.tar.gz ] ; then
  echo "ERROR: package little_brother-0.5.2.tar.gz not found in $LIB_DIR!"
  echo "Download from test.pypi.org and execute again."
  exit 2
else
  echo "Package little_brother-0.5.2.tar.gz was found."
fi

if [ ! -f $LIB_DIR/python_base_app-0.3.1.tar.gz ] ; then
  echo "ERROR: package python_base_app-0.3.1.tar.gz not found in $LIB_DIR!"
  echo "Download from test.pypi.org and execute again."
  exit 2
else
  echo "Package python_base_app-0.3.1.tar.gz was found."
fi

if [ ! -f $LIB_DIR/some_flask_helpers-0.2.8.tar.gz ] ; then
  echo "ERROR: package some_flask_helpers-0.2.8.tar.gz not found in $LIB_DIR!"
  echo "Download from test.pypi.org and execute again."
  exit 2
else
  echo "Package some_flask_helpers-0.2.8.tar.gz was found."
fi

if [ "$RUNNING_IN_DOCKER" == "" ] ; then
  mkdir -p ${SYSTEMD_DIR}
  cp ${INSTALL_BASE_DIR}/etc/little-brother.service ${SYSTEMD_DIR}/little-brother.service
fi
mkdir -p ${SUDOERS_DIR}
cp ${INSTALL_BASE_DIR}/etc/little-brother.sudo ${SUDOERS_DIR}/little-brother
mkdir -p ${APPARMOR_DIR}
cp ${INSTALL_BASE_DIR}/etc/little-brother.apparmor ${APPARMOR_DIR}/little-brother.conf
TARGET_DIRECTORY=${ROOT_DIR}/$(dirname etc/little-brother/client.config )
mkdir -p ${TARGET_DIRECTORY}
echo "Deploying extra file '$INSTALL_BASE_DIR/etc/client.config' to '${ROOT_DIR}/etc/little-brother/client.config'..."
cp -f $INSTALL_BASE_DIR/etc/client.config ${ROOT_DIR}/etc/little-brother/client.config
TARGET_DIRECTORY=${ROOT_DIR}/$(dirname etc/little-brother/master.config )
mkdir -p ${TARGET_DIRECTORY}
echo "Deploying extra file '$INSTALL_BASE_DIR/etc/master.config' to '${ROOT_DIR}/etc/little-brother/master.config'..."
cp -f $INSTALL_BASE_DIR/etc/master.config ${ROOT_DIR}/etc/little-brother/master.config





if grep -q 'little_brother:' /etc/group ; then
    echo "Group 'little_brother' already exists. Skipping group creation."
else
    #echo "Adding group 'little_brother'..."
    add_group little_brother ${APP_GID}
fi
if grep -q 'little_brother:' /etc/passwd ; then
    echo "User 'little_brother' already exists. Skipping user creation."
else
    add_user little_brother little_brother ${APP_UID}
fi

set -e
  add_user_to_group little-brother audio


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

if [ "${VIRTUAL_ENV_DIR}" != "" ] ; then

echo "Creating symbolic link /usr/local/bin/run_little_brother.py --> ${VIRTUAL_ENV_DIR}/bin/run_little_brother.py..."
ln -fs ${VIRTUAL_ENV_DIR}/bin/run_little_brother.py /usr/local/bin/run_little_brother.py
echo "Creating symbolic link /usr/local/bin/run_little_brother_test_suite.py --> ${VIRTUAL_ENV_DIR}/bin/run_little_brother_test_suite.py..."
ln -fs ${VIRTUAL_ENV_DIR}/bin/run_little_brother_test_suite.py /usr/local/bin/run_little_brother_test_suite.py
echo "Creating symbolic link /usr/local/bin/run_little_brother_test_suite_no_venv.py --> ${VIRTUAL_ENV_DIR}/bin/run_little_brother_test_suite_no_venv.py..."
ln -fs ${VIRTUAL_ENV_DIR}/bin/run_little_brother_test_suite_no_venv.py /usr/local/bin/run_little_brother_test_suite_no_venv.py

echo "Creating virtual Python environment in ${VIRTUAL_ENV_DIR}..."

virtualenv -p /usr/bin/python3 ${VIRTUAL_ENV_DIR}
echo "Activating virtual Python environment in ${VIRTUAL_ENV_DIR}..."
. ${VIRTUAL_ENV_DIR}/bin/activate
fi

echo "Setting ownership..."
echo "    * little_brother:little_brother ${ETC_DIR}"
chown -R little_brother:little_brother ${ETC_DIR}
echo "    * little_brother:little_brother ${LOG_DIR}"
chown -R little_brother:little_brother ${LOG_DIR}
echo "    * little_brother:little_brother ${SPOOL_DIR}"
chown -R little_brother:little_brother ${SPOOL_DIR}
echo "    * little_brother:little_brother ${LIB_DIR}"
chown -R little_brother:little_brother ${LIB_DIR}


echo "    * little_brother:little_brother /etc/little-brother/little-brother.config"
chown little_brother:little_brother /etc/little-brother/little-brother.config
  if [ "$RUNNING_IN_DOCKER" == "" ] ; then
  echo "    * ${SYSTEMD_DIR}/little-brother.service"
  chown root.root ${SYSTEMD_DIR}/little-brother.service
  fi
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


echo "    * little_brother:little_brother /etc/little-brother/little-brother.config"
chmod og-rwx /etc/little-brother/little-brother.config

echo "Upgrading packages 'wheel' and 'setuptools'..."
${PIP3} install wheel setuptools
echo "Installing PIP packages..."
echo "  * little_brother-0.5.2.tar.gz"
echo "  * python_base_app-0.3.1.tar.gz"
echo "  * some_flask_helpers-0.2.8.tar.gz"
# see https://stackoverflow.com/questions/19548957/can-i-force-pip-to-reinstall-the-current-version
${PIP3} install --upgrade --ignore-installed \
     ${LIB_DIR}/little_brother-0.5.2.tar.gz\
     ${LIB_DIR}/python_base_app-0.3.1.tar.gz\
     ${LIB_DIR}/some_flask_helpers-0.2.8.tar.gz

if [ "${VIRTUAL_ENV_DIR}" != "" ] ; then
  echo "Changing ownership of virtual environment ${VIRTUAL_ENV_DIR} to little_brother:little_brother..."
  chown -R little_brother:little_brother ${VIRTUAL_ENV_DIR}
fi



echo "Removing installation file ${LIB_DIR}/little_brother-0.5.2.tar.gz..."
rm ${LIB_DIR}/little_brother-0.5.2.tar.gz
echo "Removing installation file ${LIB_DIR}/python_base_app-0.3.1.tar.gz..."
rm ${LIB_DIR}/python_base_app-0.3.1.tar.gz
echo "Removing installation file ${LIB_DIR}/some_flask_helpers-0.2.8.tar.gz..."
rm ${LIB_DIR}/some_flask_helpers-0.2.8.tar.gz
if [ "$RUNNING_IN_DOCKER" == "" ] ; then
  echo "Execute systemctl daemon-reload..."
  set +e
  systemctl daemon-reload
  set -e
fi