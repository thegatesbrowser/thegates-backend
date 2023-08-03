#!/bin/bash

# Start Meilisearch
cd meilisearch
./run_meili.sh

# Move back to the parent directory and start Django server
cd ..
nohup python3 manage.py runserver 95.163.241.188:8000 &
