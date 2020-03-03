#!/bin/bash

source .env

pip install --upgrade pip
pip install requests
python3 RestQuery.py `tr '\r\n' ' ' < args.txt` -server_url http://${TOOL}:8888/REST
