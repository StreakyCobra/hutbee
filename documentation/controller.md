# Controller

This document describes the preparation and installation of the controller
Raspberry Pi. This should work out of the box with Raspberry Pi 3 and 4.

## Prepare the SD Card
 
1. Download the [`Raspberry Pi OS (32-bit) Lite`][] image. 

2. [Write the image][] to the SDCard (c.f. section «Writing the image» in the
   linked page).

3. Mount the newly created `boot` partition on your system.

4. Create an empty `ssh` file at the root of the `boot` partition. This will
   enable the `SSH` service when the Raspberry Pi starts.
 
5. Create a `wpa_supplicant.conf` file at the root of the `boot` partition. This
   will allow the Raspberry Pi to connect to your Wi-Fi when it starts. The file
   should look like this:

   ```conf
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
       ssid="Your network name"
       psk="Your network password"
   }
   ```
   
[`Raspberry Pi OS (32-bit) Lite`]: https://www.raspberrypi.org/downloads/raspberry-pi-os/
[Write the image]: https://www.raspberrypi.org/documentation/installation/installing-images/README.md

## Basic setup

1. Boot the raspberry with the prepared SD Card.

2. Connect to it by `SSH` with the help of the official [IP address][]
   documentation. Something like this may work out of the box:

   ```shell
   ssh pi@raspberrypi.local
   ```
   
   Password should be `raspberry` by default.
   
3. Update and restart the Raspberry Pi:

   ```conf
   sudo apt update
   sudo apt dist-upgrade
   sudo reboot
   ```

4. Change the `pi` password with the `passwd` command. If you want to [change
   the default username][] it's the time to do it.
   
   You may also want to disable password to run `sudo` commands, for this run
   `sudo visudo` and change the following line:
   
   ```conf
   %sudo   ALL=(ALL:ALL) NOPASSWD:ALL
   ```

5. It is recommended to change the default `SSH` port to something else than 22
   for security reasons. This can be done by uncommenting and changing the
   `Port` line in the `/etc/ssh/sshd_config` file.
   
   Other edits you may want to do are to disable root login with
   `PermitRootLogin no`, and disable password authentication with
   `PasswordAuthentication no`. For the later be sure to setup you `SSH` key
   with `ssh-copy-id` first to not be locked out.
   
6. Change the hostname to `controller` or any other name you want to identify
   this Raspberry Pi by edition the file `/etc/hostname`.
   
7. If you updated the `SSH` port, be sure to reboot so effect are applied before
   working on the firewall. 
   
   ```conf
   sudo reboot
   ```
   
   The non-default `SSH` port can be passed to the `ssh` command with `-p`.
   Remember that you just changed the hostname and potentially the username, so
   the new command will be something like:
   
   ```shell
   ssh hutbee@controller.local -p 3823
   ```

8. Installing the `ufw` firewall will add another layer of security. First
   install it with:

   ```shell script
   sudo apt install ufw
   ```
   
   then allow the SSH port you just configured:
   
   ```shell
   sudo ufw allow 3823
   ```
   
   and finally activate the firewall:
   
   ```shell
   sudo ufw enable
   ```

9. In order to have the Raspberry Pi to reconnect Wi-Fi networks when problem
   occurs, we have to create a file `/etc/network/interfaces.d/wlan0` with the
   following content:

   ```conf
   allow-hotplug wlan0
   iface wlan0 inet manual
     wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf

   iface default inet dhcp
   ```
   
10. At this point reboot the Raspberry Pi and reconnect to it to check that
    everything is still working as expected.
   
[IP address]: https://www.raspberrypi.org/documentation/remote-access/ip-address.md
[change the default username]: https://raspberrypi.stackexchange.com/a/27657

## Setup docker

1. Install docker by using their convenience script and the `docker-compose`:

   ```shell
   curl -fsSL https://get.docker.com | bash
   sudo apt install docker-compose
   ```
   
2. Add your user to the `docker` group:

   ```shell
   sudo usermod -aG docker pi
   ```
   
3. Disable docker playing with `iptables` by editing `/etc/systemd/system/multi-user.target.wants/docker.service`:

   ```conf
   ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock --iptables=false
   ```

4. Enable ufw forwarding for docker by adding this at the beginning of
   `/etc/ufw/before.rules`:

   ```conf
   *nat
   :POSTROUTING ACCEPT [0:0]
   -A POSTROUTING ! -o docker0 -s 172.16.0.0/12 -j MASQUERADE
   COMMIT
   ```
   
5. Edit `/etc/default/ufw` to allow by default the forwarding policy:

   ```shell
   DEFAULT_FORWARD_POLICY="ACCEPT"
   ```

6. Allow traffic from docker subnetworks:

   ```conf
   sudo ufw allow from 172.16.0.0/12
   ```
   
## Extra setup

1. Install byobu to have the option so detach session and keep terminal alive
   in case of network problems:

   ```shell
   sudo apt install byobu
   byobu-enable
   ```
   
   After this reconnect by `SSH` to see it in action. With this you can then
   detach a `SSH` connection with the F6 key, it will continue to run on the
   Raspberry Pi and you can come back anytime by connection with `SSH`.


## Setup hutbee

1. Install `git` and clone the `hutbee` repository:

   ```shell
   sudo apt install git
   git clone https://github.com/StreakyCobra/hutbee.git
   ```

2. Setup the `.env` file and install the `SSH` keys in the `keys` folder.

3. Start the services:

   ```shell
   docker-compose -f docker-compose.controller.yml up -d
   ```

