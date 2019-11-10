FROM ubuntu:18.04

# Update the distribution and install dependencies from the official repos
RUN apt-get update && apt-get install -y autossh \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/locale/* && rm -rf /usr/share/man/* && rm -rf /usr/share/doc/*

# Setup ssh key
COPY keys/id_rsa /root/.ssh/id_rsa

# Run autossh for a permanent connection with hutbee
CMD /usr/bin/autossh \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -o StrictHostKeyChecking=no \
  -N \
  -R 0.0.0.0:8000:controller:80 \
  -p ${ENDPOINT_SSH_PORT} \
  hutbee@${ENDPOINT_HOSTNAME} \
  -M 0
