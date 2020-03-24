#!/bin/bash

cd ../docker
docker-compose run --rm rp2paths \
  sh -c "cd test ; ./test-standalone.sh out/test-in-docker"
cd -
