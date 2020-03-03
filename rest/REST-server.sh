#!/bin/bash

command=$1

function print_help {
  echo
  echo "Usage:"
  echo -e '\t' "$0 start [flask|redis]"
  echo -e '\t' "$0 [stop|status|logs]"
  echo
}


case $command in

  "start")
    MODE=$2 docker-compose up -d
    ;;

  "stop")
    MODE="" docker-compose down -v
    ;;

  "status")
    MODE="" docker-compose ps
    ;;

  "logs")
    docker logs -f `docker inspect -f '{{.Name}}' $(MODE="" docker-compose ps -q) | cut -c2-`
    ;;

  *)
    print_help
    ;;
esac
