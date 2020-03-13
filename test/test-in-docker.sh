#!/bin/bash

cd ../docker
docker-compose run --rm rp2paths \
  bash -c 'cd test; python3 ../src/RP2paths.py all in/rp2_pathways.csv --outdir out/test-in-docker --timeout 5'
cd -
