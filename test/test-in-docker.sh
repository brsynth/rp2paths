#!/bin/bash

outdir=$1

if [[ "$outdir" == "" ]]; then
  outdir="out/test-in-docker"
fi

cd ../docker
docker-compose run --rm -v $PWD/../test:/home/test -w /home/test --entrypoint="" rp2paths \
  sh -c "./test-standalone.sh $outdir"
cd -
