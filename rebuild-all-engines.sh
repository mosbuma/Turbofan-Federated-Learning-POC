#!/bin/sh
set -e
#!/bin/bash

#build the new engine image
docker build -t turbofan-engine ./engine --no-cache;

#restart engines
for CONTAINER_NAME in engine1 engine2 engine3 engine4 engine5; do
    echo restart container $CONTAINER_NAME
    docker-compose rm --stop --force $CONTAINER_NAME; \
    docker-compose up --force-recreate -d $CONTAINER_NAME
done