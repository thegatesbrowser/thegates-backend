#!/bin/bash

# Set up the trap to catch the SIGINT signal (Ctrl-C) and call the cleanup function
cleanup() {
    echo "Cleaning up and terminating processes..."
    kill $M
    kill $S
    exit 0
}
trap cleanup SIGINT

# Start Meilisearch
cd meilisearch
./run_meili_local.sh &
M=$!

# Move back to the parent directory and start Django server
cd ..
python3 manage.py runserver 127.0.0.1:8000 &
S=$!

# Wait for both processes to finish
wait
