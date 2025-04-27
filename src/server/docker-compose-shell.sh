#!/bin/bash

# Define the path to the secrets directory
GOOGLE_CREDENTIALS_PATH=$(realpath "../../../secrets")

# Check if the credentials file exists
if [ ! -f "$GOOGLE_CREDENTIALS_PATH/secret.json" ]; then
    echo "Error: Credentials file not found at $GOOGLE_CREDENTIALS_PATH/secret.json"
    exit 1
fi

# Run Docker Compose if the check passes
docker compose up --build
