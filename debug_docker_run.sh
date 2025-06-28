#!/bin/bash

export DEBUG="true"
export SECRET="1234"
export RATE_LIMIT="50"

docker compose build
docker compose up -d