#!/bin/bash

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
# but only to python_base_app/templates/make-debian-package.template.sh!         #
##################################################################################

SCRIPT_DIR=`dirname $0`
BASE_DIR=`realpath ${SCRIPT_DIR}/..`
set -e

if [[ "littlebrother-frontend" == "None" ]] ; then
  echo "No Angular app directory defined!"
  exit 1
fi

NG_APP_DIR="${BASE_DIR}/littlebrother-frontend"

if [[ ! -d ${NG_APP_DIR} ]] ; then
  echo "Angular app directory ${NG_APP_DIR} does not exist!"
  exit 1
fi

NG_BIN="${NG_APP_DIR}/node_modules/@angular/cli/bin/ng.js"

cd ${BASE_DIR}/littlebrother-frontend

npm install
${NG_BIN} build --configuration production