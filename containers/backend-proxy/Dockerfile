FROM ubuntu:18.04

# Update the distribution and install dependencies from the official repos
RUN apt-get update && apt-get install -y autossh iproute2 \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/locale/* && rm -rf /usr/share/man/* && rm -rf /usr/share/doc/*

# Setup ssh key
COPY keys/id_rsa /root/.ssh/id_rsa

# Disable autossh connection monitoring
ENV AUTOSSH_PORT=0

# Run autossh for a permanent connection with hutbee
CMD /usr/bin/autossh \
  -o ExitOnForwardFailure=yes \
  -o ConnectTimeout=10 \
  -o ServerAliveInterval=20 \
  -o ServerAliveCountMax=3 \
  -o StrictHostKeyChecking=no \
  -R *:80:controller:80 \
  -L *:80:backend:80 \
  -R *:${CONTROLLER_SSH_PORT}:$(/sbin/ip route|awk '/default/ { print  $3}'):${CONTROLLER_SSH_PORT} \
  -N \
  -p ${CONTROLLER_PROXY_SSH_PORT} \
  ${CONTROLLER_PROXY_HOSTNAME}