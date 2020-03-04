#!/bin/bash

docker-compose run --rm -w /home/src rp2paths python RP2paths.py $@
