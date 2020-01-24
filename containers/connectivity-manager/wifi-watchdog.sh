#!/bin/bash

while true;
do
    sleep 60

    if ! timeout 30 ping -c2 "${BACKEND_HOSTNAME}" > /dev/null
    then
        echo "No connectivity, restarting wifi"
        ifconfig wlan0 down
        ifconfig wlan0 up
    else
        echo "Connectivity checked"
    fi
done
