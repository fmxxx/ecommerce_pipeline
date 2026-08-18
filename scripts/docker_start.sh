#!/bin/bash

echo "Starting rootless Docker..."
systemctl --user start docker

echo "Waiting for Docker socket..."
while [ ! -S /run/user/$(id -u)/docker.sock ]; do
    sleep 1
done

export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
echo "Rootless Docker started"
echo "DOCKER_HOST: $DOCKER_HOST"

echo "Starting docker compose..."
docker compose up -d

echo "Docker compose started successfully."
