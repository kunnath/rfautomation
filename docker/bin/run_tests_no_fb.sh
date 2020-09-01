robot --outputDir /opt/robotframework/reports ${ROBOT_OPTIONS} /opt/robotframework/tests && \
# robotmetrics -M /opt/robotframework/reports/metrics.html --inputpath /opt/robotframework/reports --logo "https://upload.wikimedia.org/wikipedia/de/7/76/Logo-smartfrog.JPG"
robotmetrics -M /opt/robotframework/reports/metrics.html --inputpath /opt/robotframework/reports --logo "https://www.ust-global.com/sites/default/files/ust-logo_dark-blue.png"
