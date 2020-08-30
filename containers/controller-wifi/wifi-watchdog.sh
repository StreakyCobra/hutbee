#!/bin/bash

while true;
do
    sleep 600

    if ! timeout 30 ping -c2 "${BACKEND_HOSTNAME}" > /dev/null
    then
        echo "No connectivity, restarting wifi"
        ifconfig wlan0 down
        sleep 10
        ifconfig wlan0 up
    else
        echo "Connectivity checked"
    fi
done
