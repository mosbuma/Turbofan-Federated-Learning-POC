#!/bin/sh
set -e

docker-compose stop engine1
docker-compose rm -f engine1
docker build -t turbofan-engine ./engine --no-cache
docker-compose build --no-cache engine1 
docker-compose up --no-deps -d engine1

docker logs engine1 --follow
