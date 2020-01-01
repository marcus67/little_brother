FROM marcusrickert/docker-minipython:release-0.9
LABEL maintainer="marcus.rickert@web.de"
COPY assets/*.deb /tmp
RUN DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            alsaplayer-alsa=0.99.81-2 \
            mpg123=1.25.10-2
RUN (dpkg -i /tmp/*.deb || true) && \
    DEBIAN_FRONTEND=noninteractive \
        apt-get install -f -y --no-install-recommends
