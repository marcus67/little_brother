#    Copyright (C) 2019-2022  Marcus Rickert
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

# Note on the installation of libldap-2.4.59-2-x86_64.pkg.tar.zst: The current version of libldap does not supply
# the librnary ldap_r anymore but the current Python package python_ldap still depends on it. So the compilation of
# the Pip package fails. We have to use an older version of libldap to make it work!

FROM archlinux:base
LABEL maintainer="marcus.rickert@web.de"
RUN pacman -Sy && \
    pacman -S  sudo \
               python3 \
               python-pip \
               python-virtualenv \
               cmake \
               gcc \
               curl \
               unzip \
               --noconfirm
