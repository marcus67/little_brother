FROM marcusrickert/docker-minipython:release-0.9
#FROM accso/docker-python-app:latest
LABEL maintainer="marcus.rickert@web.de"
COPY assets/*.deb /tmp
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends alsaplayer-alsa mpg123
#COPY assets/pulse-client.conf /etc/pulse/pulse-client.conf
RUN (dpkg -i /tmp/*.deb || true)\
    && DEBIAN_FRONTEND=noninteractive apt-get install -f -y --no-install-recommends
