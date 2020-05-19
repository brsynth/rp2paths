#!/bin/bash

infile=$1
outdir=$2

cd ../docker
docker-compose run --rm -v $PWD/../test:/home/test -w /home/test --entrypoint="" rp2paths \
  sh -c "./run.sh $infile $outdir"
cd -
