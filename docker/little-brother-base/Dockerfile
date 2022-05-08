FROM marcusrickert/docker-minipython:release-0.9
LABEL maintainer="marcus.rickert@web.de"
ENV RUNNING_IN_DOCKER=1
COPY assets/*.deb /tmp
# See https://superuser.com/questions/1456989/how-to-configure-apt-in-debian-buster-after-release
RUN DEBIAN_FRONTEND=noninteractive \
        apt-get update --allow-releaseinfo-change && \
        apt-get install -y --no-install-recommends
RUN (dpkg -i /tmp/*.deb || true) && \
    DEBIAN_FRONTEND=noninteractive \
        apt-get install -f -y --no-install-recommends
