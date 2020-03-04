#!/bin/bash

pip install --upgrade pip
pip install requests
python3 files/RestQuery.py `tr '\r\n' ' ' < files/args.txt` -server_url http://rp2paths:8888/REST
