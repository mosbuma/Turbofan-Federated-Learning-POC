#!/bin/sh

set -e

#local versions of these images are used
docker build -t turbofan-engine ./engine
docker build -t pysyft-notebook ./pysyft-notebook

# docker build -t syft-base ./docker_syft_base
docker build -t turbofan-federated-trainer ./federated_trainer
docker build -t amdex_server ./amdex_server

