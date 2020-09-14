#!/bin/bash

source ../extras/.env

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f check/docker/docker-compose.yml \
    --env-file check/docker/.env \
    build

# Pass the engine to be processed by check, if empty all modes will be processed
if [[ $# -gt 0 ]]; then
  mod=$1
else
  mod=$@
fi


PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f check/docker/docker-compose.yml \
    --env-file check/docker/.env \
  run --rm \
  flake$mod

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f check/docker/docker-compose.yml \
    --env-file check/docker/.env \
  run --rm \
  bandit
