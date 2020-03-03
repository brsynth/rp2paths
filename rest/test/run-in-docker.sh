#!/bin/bash

source .env

docker run --rm \
  --link ${TOOL}-rest:${TOOL} \
  -v $PWD:/home \
  -w /home \
  --net ${TOOL} \
python:3 ./run.sh
