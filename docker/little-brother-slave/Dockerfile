ARG TAG
ARG DOCKER_REGISTRY_ORG_UNIT
FROM $DOCKER_REGISTRY_ORG_UNIT/little-brother-base:$TAG
LABEL maintainer="marcus.rickert@web.de"
ENV MASTER_HOST_URL=http://localhost:5555
ENV MASTER_ACCESS_TOKEN=SOME_LONG_AND_SECRET_TOKEN
COPY assets/entrypoint.sh /entrypoint.sh
COPY assets/little-brother.config /etc
ENTRYPOINT ["/entrypoint.sh"]
CMD []
USER little-brother
