#!/bin/sh

set -e

docker-compose down
docker image prune -a --force --filter "label!=heurekalabs/grid-gateway"
./build-docker-images.sh
docker-compose up