#!/bin/sh

if [ "$DEBUG" == "true" ]; then
    echo "Running in debug mode"
    poetry run python3 -m src.main
else
    echo "Not running in debug mode"
    poetry run python3 -m gunicorn -b 0.0.0.0:8080 src.main:app
fi