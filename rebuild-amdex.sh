#!/bin/bash

#build the new engine image
docker build -t amdex_server ./amdex_server --no-cache;

#restart engines
for CONTAINER_NAME in amdex_server; do 
    echo restart container $CONTAINER_NAME
    docker-compose rm --stop --force $CONTAINER_NAME; \
    docker-compose up --force-recreate -d $CONTAINER_NAME
done