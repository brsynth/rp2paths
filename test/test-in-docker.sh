#!/bin/bash

cd ../docker
docker-compose run --rm -v $PWD/../test:/home/test -w /home/test --entrypoint="" rp2paths \
  sh -c "./test-standalone.sh out/test-in-docker"
cd -
