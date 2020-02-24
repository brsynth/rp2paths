#!/bin/bash

command=`cat run.sh`

docker run --rm \
  -v $PWD/..:/home \
  -v $PWD:/home/test \
  -w /home/test \
brsynth/rp2paths bash -c "$command"
