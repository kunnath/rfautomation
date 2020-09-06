#!/bin/bash

nohup /usr/bin/appium > /dev/null &

adb devices 
adb tcpip 5555 
adb devices 

sleep 5 

robot --outputDir /opt/robotframework/reports ${ROBOT_OPTIONS} /opt/robotframework/tests && \
robotmetrics -M /opt/robotframework/reports/metrics.html --inputpath /opt/robotframework/reports --logo "https://upload.wikimedia.org/wikipedia/de/7/76/Logo-smartfrog.JPG"
