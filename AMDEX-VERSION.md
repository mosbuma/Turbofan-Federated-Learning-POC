# AMDEX version of the Turbofan Federated Learning POC

# changes to the original POC

- engine node - remove scheduler, implement AMDEX functionality
- jupyter node - add standard password "amdex_rulez"

# progress

## setup the environment on a local machine

- install docker + docker compose
- execute ./build-docker-images.sh to create images that are modified for the AMDEX POC (engine, pysyft-notebooks)
- run docker-compose up -d to start the POC virtual environment
- run

## setup the environment on a remote VSP

- use the scripts from setup folder (outside this folder) to create an instance and setup the instance:
  - create-instances.sh
  - setup-instances.sh
  - delete-instances.sh

## setup local images for AMDEX modifications

- bashscripts that restart individual / groups of containers for debugging:
  - rebuild-engine1.sh
  - rebuild-all-engines.sh
  - rebuild-trainer.sh

### jupyter node - jupyter node - add standard password "amdex_rulez"

- option "-NotebookApp.token='amdex_rulez'" added to entrypoint.sh

### engine node

- removed scheduler
- use http://<node ip>:800X/process to start creating data for training / testing (X = engine number)
- docker logs engineX --follow for logging
