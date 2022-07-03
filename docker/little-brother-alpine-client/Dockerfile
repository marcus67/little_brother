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

FROM alpine:latest
LABEL maintainer="marcus.rickert@web.de"
ARG BRANCH
ARG REPO_DOWNLOAD_BASE_URL
ARG TEST_PYPI_EXTRA_INDEX
ENV MASTER_HOST_URL=http://localhost:5555
ENV MASTER_ACCESS_TOKEN=SOME_LONG_AND_SECRET_TOKEN
ENV RUNNING_IN_DOCKER=1
RUN apk update && \
    apk add bash \
            sudo \
            python3 \
            python3-dev \
            py3-pip \
            py3-packaging \
            unzip \
            linux-headers \
            build-base \
            gcc \
            curl && \
    pip install --upgrade pip && \
    curl -L ${REPO_DOWNLOAD_BASE_URL}${BRANCH}.zip -o /tmp/repo.zip -o /tmp/repo.zip && \
    cd /tmp && \
    unzip /tmp/repo.zip && \
    /tmp/little_brother-*/bin/generic-install.sh && \
    rm -rf /tmp/little_brother-* && \
    rm -f /tmp/*.apk && \
    rm -f /tmp/repo.zip && \
    apk del py3-pip \
            python3-dev \
            build-base \
            linux-headers \
            unzip \
            gcc
COPY assets/entrypoint.sh /entrypoint.sh
COPY assets/little-brother.config /etc
ENTRYPOINT ["/entrypoint.sh"]
CMD []
USER little-brother
