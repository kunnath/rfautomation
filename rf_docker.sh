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
ROBOT_OPTIONS="${ROBOT_OPTIONS} -x results.junit.xml"

if [ -z "$PS1" ]; then
  DOCKER_OPTIONS="-it"
else
  DOCKER_OPTIONS=""
fi

mkdir -p artifact_store

if [[ $1 == "automation" ]]; then

 docker run --rm $RUN_ARGS \
    --shm-size 5g \
    -v "$this_path/tests":/opt/robotframework/tests:Z \
    -v "$this_path/reports":/opt/robotframework/reports:Z \
    -v "$this_path/artifact_store":/opt/robotframework/artifact_store:Z \
    -v "$this_path/variables":/opt/robotframework/variables:Z \
    -v "$this_path/keywords":/opt/robotframework/keywords:Z \
    -e ROBOT_OPTIONS="${ROBOT_OPTIONS}" \
    -e BROWSER="${BROWSER:-chrome}" \
    "rfdocker:$BUILD_NAME"
fi
