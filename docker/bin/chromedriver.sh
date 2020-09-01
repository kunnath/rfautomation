#!/bin/sh
# /usr/bin/chromedriver --verbose --log-path=/var/log/chromedriver --no-sandbox --user-data-dir=/home/user --disable-dev-shm-usage $@
/usr/bin/chromedriver --verbose --log-path=/opt/robotframework/chromedriver.log --no-sandbox --user-data-dir=/home/user --disable-dev-shm-usage $@