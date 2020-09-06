#!/usr/bin/env bash
# https://github.com/asyrjasalo/rfdocker
# https://hub.docker.com/r/robotframework/rfdocker

set -e

if [ "$DEBUG" == "" ]; then
  set -x
fi

### constants ##################################################################

this_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

### variables ##################################################################

: ${BUILD_ARGS:=""}
: ${BUILD_DIR:="$this_path"}
: ${BUILD_NAME:=${this_path##*/}}
: ${RUN_ARGS:=''}

### build and run ##############################################################

if [[ -z "$BUILD_ROBOT_DOCKER" ]]; then
  docker build $BUILD_ARGS --tag "rfdocker:$BUILD_NAME" "$BUILD_DIR"
fi
if [[ $1 == "perf" ]]; then
  docker pull "blazemeter/taurus"
  PERF_TESTS=true
  export perf_scripts="${PWD}/perf/perf_scripts"
  export perf_artifacts="${PWD}/perf/perf_artifacts"
fi

if [[ $1 == "mobile" ]]; then
  MOBILE_TESTS=true
  ROBOT_OPTIONS="${ROBOT_OPTIONS} -i android"
  shift
elif [[ $1 == "api" ]]; then
  STREAMING_TESTS=true
  ROBOT_OPTIONS="${ROBOT_OPTIONS} -i api"
  shift
fi

ROBOT_OPTIONS="${ROBOT_OPTIONS} -x results.junit.xml"

if [ -z "$PS1" ]; then
  DOCKER_OPTIONS="-it"
else
  DOCKER_OPTIONS=""
fi

mkdir -p artifact_store

if [[ $1 == "manual" ]]; then
  export BUILD_NAME
  export ROBOT_OPTIONS
  export DOCKER_OPTIONS
  ${this_path}/scripts/manual-test.sh
  
elif [[ $MOBILE_TESTS == "true" ]]; then
  docker run $DOCKER_OPTIONS --rm $RUN_ARGS \
    --privileged -v /dev/bus/usb:/dev/bus/usb \
    --shm-size 5g \
    -v "$this_path/tests":/opt/robotframework/tests:Z \
    -v "$this_path/reports":/opt/robotframework/reports:Z \
    -v "$this_path/artifact_store":/opt/robotframework/artifact_store:Z \
    -v "$this_path/variables":/opt/robotframework/variables:Z \
    -v "$this_path/keywords":/opt/robotframework/keywords:Z \
    -e ROBOT_OPTIONS="${ROBOT_OPTIONS}" \
    "rfdocker:$BUILD_NAME" \
    bash -x /opt/robotframework/bin/run_appium.sh

elif [[ $STREAMING_TESTS == "true" ]]; then
  docker run $DOCKER_OPTIONS --rm $RUN_ARGS \
    --shm-size 3g \
    -v "$this_path/tests/apirobot":/opt/robotframework/tests/apirobot:Z \
    -v "$this_path/reports":/opt/robotframework/reports:Z \
    -v "$this_path/artifact_store":/opt/robotframework/artifact_store:Z \
    -v "$this_path/variables":/opt/robotframework/variables:Z \
    -v "$this_path/keywords":/opt/robotframework/keywords:Z \
    -e ROBOT_OPTIONS="${ROBOT_OPTIONS}" \
    -e BROWSER="${BROWSER:-chrome}" \
    "rfdocker:$BUILD_NAME"

elif [[ $PERF_TESTS == "true" ]]; then
  docker run $DOCKER_OPTIONS --rm \
    -v ${perf_scripts}:/bzt-configs \
    -v ${perf_artifacts}:/tmp/artifacts \
  blazemeter/taurus ${perf_scripts}/test.yml

else
  docker run --rm $RUN_ARGS \
    --shm-size 5g \
    -v "$this_path/tests":/opt/robotframework/tests:Z \
    -v "$this_path/tests/streaming/scripts":/opt/robotframework/tests/streaming/scripts:Z \
    -v "$this_path/reports":/opt/robotframework/reports:Z \
    -v "$this_path/artifact_store":/opt/robotframework/artifact_store:Z \
    -v "$this_path/variables":/opt/robotframework/variables:Z \
    -v "$this_path/keywords":/opt/robotframework/keywords:Z \
    -e ROBOT_OPTIONS="${ROBOT_OPTIONS}" \
    -e BROWSER="${BROWSER:-chrome}" \
    "rfdocker:$BUILD_NAME"
fi
