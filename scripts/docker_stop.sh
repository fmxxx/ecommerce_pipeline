#!/bin/bash

echo "Stopping docker compose..."
docker compose down

echo "Docker compose stopped successfully."

echo "Stopping Docker daemon..."
if command -v systemctl > /dev/null 2>&1; then
    sudo systemctl stop docker
elif command -v service > /dev/null 2>&1; then
    sudo service docker stop
fi
echo "Docker daemon stopped."
