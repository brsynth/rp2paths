#!/bin/bash

cd ../docker
docker-compose run --rm rp2paths \
  bash -c "cd test ; ./test-standalone.sh"
cd -
