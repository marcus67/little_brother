#    Copyright (C) 2019-2025  Marcus Rickert
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

# See https://stackoverflow.com/questions/70182720/python-ldap-3-4-installation-fails-on-alpine-images

FROM alpine:3.18.2
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
            py3-packaging \
            py3-virtualenv \
            py3-pip \
            py3-virtualenv \
            unzip \
            linux-headers \
            build-base \
            gcc \
            musl-dev \
            libffi-dev \
            openldap-dev \
            openssl-dev \
            curl && \
    pip install --ignore-installed --upgrade pip && \
    curl -L ${REPO_DOWNLOAD_BASE_URL}${BRANCH}.zip -o /tmp/repo.zip && \
    cd /tmp && \
    unzip /tmp/repo.zip && \
    /tmp/little_brother-*/bin/generic-install.sh && \
    echo 'INPUT ( libldap.so )' > /usr/lib/libldap_r.so && \
    pip install --ignore-installed python-base-app-ldap-extension>=0.1.4 && \
    rm -rf /tmp/little_brother-* && \
    rm -f /tmp/*.apk && \
    rm -f /tmp/repo.zip && \
    apk del py3-pip \
            python3-dev \
            musl-dev \
            libffi-dev \
            openldap-dev \
            openssl-dev \
            build-base \
            linux-headers \
            unzip \
            gcc
COPY assets/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD []
USER little-brother
