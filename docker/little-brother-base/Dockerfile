FROM marcusrickert/docker-minipython:latest
LABEL maintainer="marcus.rickert@web.de"
COPY assets/*.deb /tmp
RUN dpkg -i /tmp/*.deb \
    && DEBIAN_FRONTEND=noninteractive apt-get install -f -y --no-install-recommends
