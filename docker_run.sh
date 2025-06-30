#!/bin/bash

export DEBUG="false"

if ! [[ -n "$SECRET" ]]; then

printf "Error: No secret (SECRET) set\n"
exit 1

fi

if ! [[ -n "$RATE_LIMIT" ]]; then

printf "Error: No rate limit (RATE_LIMIT) set\n"
exit 1

fi

if ! [[ -n "$HOST" ]]; then

printf "Error: No host (HOST) set\n"
exit 1

fi

docker compose build
docker compose up -d