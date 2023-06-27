#!/bin/bash
#exec gunicorn -b=:${PORT} --config /app/gunicorn.conf -k flask_sockets.worker --chdir /app/grid_node websocket_app:app &
export GRID_NETWORK_URL=http://grid-gateway:5000
export ID=gridnode1
export ADDRESS=http://engine1:8001
export DATABASE_URL=sqlite:///databaseGridEngine1.db
export PORT=4001
export ENGINE_ID=engine1
export ENGINE_PORT=8001
export GRID_NODE_ADDRESS=localhost:4001
export GRID_GATEWAY_ADDRESS=grid-gateway:5000
export DATA_DIR=/data
export DATASET_ID=1
export CYCLE_LENGTH=2
export GUNICORN_WORKER_CLASS=gevent
export GUNICORN_TIMEOUT=10
export GUNICORN_GRACEFUL_TIMEOUT=2
#GUNICORN_LOG\-FILE=\-

echo got engine port $ENGINE_PORT

gunicorn -b=:${ENGINE_PORT} --config ./gunicorn.conf --log-config ../logging.conf -k flask_sockets.worker --chdir ./engine_node turbofan_worker:app
