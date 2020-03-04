#!/bin/bash

cd ../docker
docker-compose run --rm \
  -v $PWD/../test:/home/test \
rp2paths \
  bash -c "cd test ; ./test-standalone.sh"
cd -
