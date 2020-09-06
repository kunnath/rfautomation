#!/bin/bash -x
set -xv   # this line will enable debug
appium --address $1 --port 4723 --no-reset
