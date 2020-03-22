#!/bin/bash


# cd ../rest
# ./REST-server.sh start redis
# cd -
#
# sleep 5

docker run --rm \
  -v $PWD:/home \
  -w /home \
  --net rp2paths \
python:3 ./files/rest-query.sh


# cd ../rest
# ./REST-server.sh stop
# cd -
