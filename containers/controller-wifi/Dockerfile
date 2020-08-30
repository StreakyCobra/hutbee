FROM ubuntu:18.04

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    net-tools \
    iputils-ping \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/locale/* /usr/share/man/* /usr/share/doc/*

COPY containers/controller-wifi/wifi-watchdog.sh /usr/local/bin/wifi-watchdog.sh
RUN chmod +x /usr/local/bin/wifi-watchdog.sh

CMD /usr/local/bin/wifi-watchdog.sh
