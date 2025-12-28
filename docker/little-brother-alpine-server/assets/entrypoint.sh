#!/usr/bin/env bash
#    Copyright (C) 2019-2024  Marcus Rickert
#
#    See https://github.com/marcus67/little_brother
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

echo "Starting Little-Brother in server mode..."

CONFIG_FILE=/etc/little-brother.config
LOGLEVEL=${LOGLEVEL:-INFO}
ALEMBIC_TARGET=${ALEMBIC_TARGET:-head}
#LOGDIR=/var/log/little-brother

if [ ! -f "${CONFIG_FILE}" ] ; then
  echo "ERROR: No configuration file found at ${CONFIG_FILE}. Please mount a valid file into the container!"
  exit 1
fi

#if grep -qs "^[^ ]\+ \+${LOGDIR}\( \|$\)" /proc/mounts; then
#    echo "The log directory '${LOGDIR}' has been mounted from outside the container -> excellent!"
#else
#    echo "Directory '${LOGDIR}' is a local to the container. Container mounting a host directory onto ${LOGDIR}!"
#fi

echo "Executing the following expanded command:"
set -x
exec run_little_brother.py \
           --config /etc/little-brother.config \
           --pidfile=/run/little-brother/little-brother.pid \
           --loglevel "${LOGLEVEL}" \
           --create-databases \
           --upgrade-databases="${ALEMBIC_TARGET}"
