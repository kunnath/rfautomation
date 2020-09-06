#!/usr/bin/env bash
# set -e
docker-compose down        
docker rm -fv $(docker ps -aq)
sudo lsof -i -P -n | grep 5432
