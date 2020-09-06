#!/bin/bash -x
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOROOT_DIR="$(cd ${SCRIPT_DIR}/../ && pwd)"
BUILD_NAME=$(basename $(dirname ${SCRIPT_DIR}))
: ${SSH_PORT:=53436}
: ${ROBOT_OPTIONS:=""}

#
# Run docker as daemon
#
TARGET_CONTAINER=$(docker run --rm --user $(id -u):$(id -g) $RUN_ARGS \
                          --shm-size 5g \
                          -v "$REPOROOT_DIR/tests":/opt/robotframework/tests:Z \
                          -v "$REPOROOT_DIR/reports":/opt/robotframework/reports:Z \
                          -v "$REPOROOT_DIR/variables":/opt/robotframework/variables:Z \
                          -v "$REPOROOT_DIR/keywords":/opt/robotframework/keywords:Z \
                          -p ${SSH_PORT}:22/tcp -itd \
                          -e BROWSER="${BROWSER:-chrome}" \
                          "rfdocker:$BUILD_NAME" /bin/bash)

[[ $? -ne 0 ]] && { >&2 echo "failed to launch docker container"; exit 1; }

# Setup SSHD configuration
#
docker cp ${TARGET_CONTAINER}:/root/.ssh/robot_manual_test_key ~/.ssh/
chmod 600 ~/.ssh/robot_manual_test_key

user_uid=$(id -u)
user_gid=$(id -g)

docker exec -u 0:0 -it ${TARGET_CONTAINER} /bin/sh -c "groupadd -g ${user_gid} robot_manual; useradd -u ${user_uid} -g ${user_gid} robot_manual -m -d /home/robot_manual; mkdir -p /home/robot_manual/.ssh; cp /root/.ssh/authorized_keys /home/robot_manual/.ssh/; chmod 600 /home/robot_manual/.ssh/authorized_keys; chown -R ${user_uid}:${user_gid} /home/robot_manual"

docker exec -u 0:0 -it ${TARGET_CONTAINER} /bin/sh -c "/usr/sbin/sshd -o AuthenticationMethods=publickey -o X11Forwarding=yes -o X11UseLocalhost=yes -o AddressFamily=inet; sleep 3.5"


#
# Run SSH
#
ssh-keygen -f ~/.ssh/known_hosts -R '[localhost]:'${SSH_PORT}
## ssh -Y -A -i ~/.ssh/robot_manual_test_key -p ${SSH_PORT} -l robot_manual localhost xeyes # test x11
export ROBOT_OPTIONS="${ROBOT_OPTIONS} -i manual -e deprecated -v IS_MANUAL:True"
ssh -Y -A -o StrictHostKeyChecking=no -o SendEnv=ROBOT_OPTIONS -i ~/.ssh/robot_manual_test_key -p ${SSH_PORT} -l robot_manual localhost 'robot --outputDir /opt/robotframework/reports '"${ROBOT_OPTIONS}"' /opt/robotframework/tests; robotmetrics -M /opt/robotframework/reports/metrics.html --inputpath /opt/robotframework/reports --logo "https://upload.wikimedia.org/wikipedia/de/7/76/Logo-smartfrog.JPG"'
#docker kill ${TARGET_CONTAINER} # kill container once it's finished
