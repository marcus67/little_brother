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
ARG TAG
ARG DOCKER_REGISTRY_ORG_UNIT
FROM $DOCKER_REGISTRY_ORG_UNIT/little-brother-ubuntu-base:$TAG
LABEL maintainer="marcus.rickert@web.de"
ENV MASTER_HOST_URL=http://localhost:5555
ENV MASTER_ACCESS_TOKEN=SOME_LONG_AND_SECRET_TOKEN
COPY assets/entrypoint.sh /entrypoint.sh
COPY assets/little-brother.config /etc
ENTRYPOINT ["/entrypoint.sh"]
CMD []
USER little-brother
