#!/bin/bash -x
set -xv   # this line will enable debug

adbconnectdisconnect() {
adb disconnect
adb tcpip $1
sleep 3
IP=$(adb shell ip addr show wlan0  | grep 'inet ' | cut -d' ' -f6| cut -d/ -f1)
echo "${IP}"
export Device_id=${IP}
echo $Device_id
adb connect $IP:$1

return  "$IP:$1"
}


# adbconnectdisconnect $1

mystr=$(adbconnectdisconnect $1)
echo "$mystr"