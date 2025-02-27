
# robotmetrics -M /opt/robotframework/reports/metrics.html --inputpath /opt/robotframework/reports --logo "https://upload.wikimedia.org/wikipedia/de/7/76/Logo-smartfrog.JPG"
robot  --loglevel DEBUG --outputDir ./reports ${ROBOT_OPTIONS} ./tests/mainwebsite && \
robotmetrics -M ./metrics.html --inputpath ./reports