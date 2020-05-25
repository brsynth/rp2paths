#!/bin/bash

cd ../docker
docker-compose run --rm -v $PWD/../test:/home/test -w /home/test --entrypoint="" rp2paths \
  sh -c "./run.sh"
cd - > /dev/null
