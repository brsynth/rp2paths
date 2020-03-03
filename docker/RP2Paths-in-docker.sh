#!/bin/bash

docker run --rm \
  -v $PWD/../src:/home/src \
  -v $PWD/../examples:/home/examples \
  -w /home \
  brsynth/rp2paths \
bash -c "python src/RP2paths.py $@"
