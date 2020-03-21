#!/bin/bash

pip install --upgrade pip
pip install requests
python3 files/RestQuery.py `tr '\r\n' ' ' < files/args.txt` -server_url http://flask:8000/rp2paths
