#!/bin/bash

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

SCRIPT_DIR=$(dirname $0)
BASE_DIR=$(realpath ${SCRIPT_DIR}/..)

if [ ! "${VIRTUALENV}" == "" ]; then
    source ${VIRTUALENV}/bin/activate
fi

PATH=${PATH}:${HOME}/.virtualenvs/little-brother/bin
echo "Enter LOCALE:"
read LOCALE
pybabel init -i ${BASE_DIR}/etc/messages.pot -d ${BASE_DIR}/little_brother/translations -l ${LOCALE}
