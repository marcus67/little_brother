ARG TAG
FROM marcusrickert/little-brother-base:$TAG
MAINTAINER marcus.rickert@web.de
ENV MASTER_HOST_URL=http://localhost:5560
ENV MASTER_ACCESS_TOKEN=SOME_LONG_AND_SECRET_TOKEN
COPY assets/entrypoint.sh /entrypoint.sh
COPY assets/little-brother.config /etc
ENTRYPOINT ["/entrypoint.sh"]
CMD []
