FROM ubuntu:20.04

# Update the distribution and install dependencies from the official repos
RUN apt-get update && apt-get install -y openssh-server \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/locale/* /usr/share/man/* /usr/share/doc/*

ARG CONTROLLER_PROXY_SSH_PORT

# Setup ssh daemon
RUN mkdir -p /run/sshd
RUN sed -i "s/#Port 22/Port ${CONTROLLER_PROXY_SSH_PORT}/" /etc/ssh/sshd_config
RUN sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/" /etc/ssh/sshd_config
RUN sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
RUN sed -i "s/#GatewayPorts no/GatewayPorts clientspecified/" /etc/ssh/sshd_config
RUN sed -i "s/#ClientAliveInterval 0/ClientAliveInterval 20/" /etc/ssh/sshd_config
RUN sed -i "s/#ClientAliveCountMax 3/ClientAliveCountMax 3/" /etc/ssh/sshd_config

# Copy allowed ssh key
COPY keys/id_rsa.pub /root/.ssh/authorized_keys

# Tell traefik what port to use
EXPOSE 80

# Start ssh server in foreground
CMD /usr/sbin/sshd -D
