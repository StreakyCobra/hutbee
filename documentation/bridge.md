# Bridge

This document describes the preparation and installation of the Wi-Fi bridge
Raspberry Pi. This should work out of the box with Raspberry Pi 3 and 4.

## Prepare the Raspbery Pi

Follow first 2 sections of the [controller documentation](controller.md):

- Prepare the SD Card
- Basic setup

## Setup bridge

- Install `dnsmasq` with `sudo apt install dnsmasq`.

- Configure DHCP in `/etc/dhcpcd.conf`:

  ```conf
  interface eth0
  static ip_address=192.168.220.1/24
  static routers=192.168.220.0
  ```
  
  and restart the service with `sudo service dhcpcd restart`.
  
- Backup `dnsmasq.conf`:

  ```shell
  sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
  ```
  
- Edit `/etc/dnsmasq.conf`:

  ```conf
  interface=eth0
  listen-address=192.168.220.1
  bind-dynamic
  server=192.168.220.1@wlan0
  bogus-priv
  domain-needed
  dhcp-range=192.168.220.50,192.168.220.150,12h
  ```
  
- Enable IP forwarding by editing `/etc/systctl.conf` by uncommenting:

  ```conf
  net.ipv4.ip_forward=1
  net.ipv6.conf.all.forwarding=1
  ```
  
- Edit `/etc/default/ufw` to allow by default the forwarding policy:

  ```shell
  default_forward_policy="accept"
  ```

- Setup forwarding from eth0 to wlan0:

  ```conf
  sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE  
  sudo iptables -A FORWARD -i wlan0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT  
  sudo iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT 
  ```
  
- Allow traffic in the firewall

  ```conf
  sudo ufw allow in on eth0 from any to any port 53
  sudo ufw allow in on eth0 from any to any port 67
  ```
   
