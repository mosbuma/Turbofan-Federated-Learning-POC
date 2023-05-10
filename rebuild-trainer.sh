#!/bin/bash

#build the new engine image
# --no-cache
docker build -t trainer ./federated_trainer

#restart engines
for CONTAINER_NAME in trainer; do  # engine2 engine3 engine4 engine5
    echo restart container $CONTAINER_NAME
    docker-compose rm --stop --force $CONTAINER_NAME; \
    docker-compose up --force-recreate -d $CONTAINER_NAME
done