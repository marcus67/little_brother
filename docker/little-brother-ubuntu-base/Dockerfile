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
FROM marcusrickert/docker-ubuntu-minipython:release-0.9.1
LABEL maintainer="marcus.rickert@web.de"
ENV RUNNING_IN_DOCKER=1
COPY assets/*.deb /tmp
# See https://superuser.com/questions/1456989/how-to-configure-apt-in-debian-buster-after-release
RUN DEBIAN_FRONTEND=noninteractive \
        apt-get update --allow-releaseinfo-change && \
        apt-get install -y --no-install-recommends \
            alsaplayer-alsa \
            mpg123
RUN (dpkg -i /tmp/*.deb || true) && \
    DEBIAN_FRONTEND=noninteractive \
        apt-get install -f -y --no-install-recommends
