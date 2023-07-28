#!/bin/bash

#    Copyright (C) 2019-2022  Marcus Rickert
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
# but only to python_base_app/templates/pip3.template.sh!                        #
##################################################################################

if [ "${VIRTUAL_ENV_DIR}" == "" ] ; then
  if [ -x /usr/local/bin/pip3 ] ; then
    # If there is a pip in /usr/local it has probably been in installed/upgraded by pip itself.
    # We had better take this one...
    PIP3=/usr/local/bin/pip3
  else
    # Otherwise take the one that has been installed by the Debian package...
    PIP3=/usr/bin/pip3
  fi
else
  echo "Detected virtual environment at ${VIRTUAL_ENV_DIR}..."
  PIP3=${VIRTUAL_ENV_DIR}/bin/pip3
fi

if [ "${PIP3}" == "" ] ; then
  echo "ERROR: cannot find pip3!"
  exit 1
fi

EXTRA_INDEX_URL="$TEST_PYPI_EXTRA_INDEX"


if [ "${EXTRA_INDEX_URL}" == "" ] ; then
  echo "No extra PIP indexes defined!"
  EXTRA_INDEX_OPTION=
else
  echo "Detected extra pip index URL: ${EXTRA_INDEX_URL}"
  PROTOCOL=$(echo ${EXTRA_INDEX_URL}|sed -n -e 's/\(^https\?\):\/\/\([^\/]*\)\/\(.*\)/\1/p')
  INDEX_HOST=$(echo ${EXTRA_INDEX_URL}|sed -n -e 's/\(^https\?\):\/\/\([^\/]*\)\/\(.*\)/\2/p')
  INDEX_REL_URL=$(echo ${EXTRA_INDEX_URL}|sed -n -e 's/\(^https\?\):\/\/\([^\/]*\)\/\(.*\)/\3/p')

  if [ "${TEST_PYPI_API_TOKEN}" == "" ] ; then
    EXTRA_INDEX_OPTION="--extra-index-url ${PROTOCOL}://${TEST_PYPI_API_USER}:${TEST_PYPI_API_TOKEN}@${INDEX_HOST}/${INDEX_REL_URL}"
  else
    if [ "${TEST_PYPI_API_USER}" == "" ] ; then
      echo "WARNING: TEST_PYPI_API_USER is not set! Will default to '__token__'."
      TEST_PYPI_API_USER="__token__"
    fi
    echo "Using user '${TEST_PYPI_API_USER}' to access PiPy index..."
    EXTRA_INDEX_OPTION="--extra-index-url ${PROTOCOL}://${TEST_PYPI_API_USER}:${TEST_PYPI_API_TOKEN}@${INDEX_HOST}/${INDEX_REL_URL}"
  fi

  if [ "${PROTOCOL}" == "http" ] ; then
    echo "Adding trusted-host option for non-HTTPS host '${INDEX_HOST}'..."
    EXTRA_INDEX_OPTION+=" --trusted-host ${INDEX_HOST}"
  fi
fi

echo "Using pip3 binary at ${PIP3}..."
${PIP3} $@ ${EXTRA_INDEX_OPTION}