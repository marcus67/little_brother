FROM bitnami/minideb:buster
LABEL maintainer="marcus.rickert@web.de"
COPY assets/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir -p /deb_root
ENTRYPOINT ["/entrypoint.sh"]
CMD []
