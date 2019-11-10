FROM ubuntu:18.04

# Update the distribution and install dependencies from the official repos
RUN apt-get update && apt-get install -y openssh-server \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/locale/* && rm -rf /usr/share/man/* && rm -rf /usr/share/doc/*

# Setup ssh daemon
RUN mkdir -p /run/sshd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
RUN sed -i 's/#GatewayPorts no/GatewayPorts clientspecified/' /etc/ssh/sshd_config

# Setup user and ssh key
RUN useradd -m -s /bin/bash hutbee
COPY keys/id_rsa.pub /home/hutbee/.ssh/authorized_keys

# Tell traefik what port to use
EXPOSE 8000

# Start ssh in foreground
CMD /usr/sbin/sshd -D
