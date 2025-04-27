#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define constants
export IMAGE_NAME="backend-app"
export BASE_DIR=$(pwd)
export ENV_FILE_PATH=$(realpath "../.env") # Path to the .env file in the env folder
export GOOGLE_CREDENTIALS_PATH=$(realpath "../../../../secrets")

# Check if the credentials file exists
if [ ! -f "$GOOGLE_CREDENTIALS_PATH/secret.json" ]; then
    echo "Error: Credentials file not found at $GOOGLE_CREDENTIALS_PATH/secret.json"
    exit 1
fi

# Ensure the .env file exists
if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "Error: .env file not found at $ENV_FILE_PATH"
    exit 1
fi

# Load APP_PORT_BACKEND from the .env file
APP_PORT_BACKEND=$(grep APP_PORT_BACKEND "$ENV_FILE_PATH" | cut -d '=' -f2)

# Ensure APP_PORT_BACKEND is set
if [ -z "$APP_PORT_BACKEND" ]; then
    echo "Error: APP_PORT_BACKEND not set in $ENV_FILE_PATH"
    exit 1
fi

# Determine if /bin/bash is passed as an argument
if [ "$1" == "/bin/bash" ]; then
    CMD="/bin/bash"
else
    CMD=""
fi

# Build the Docker image
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the Docker container
docker run --rm --name "${IMAGE_NAME}-shell" -ti \
    --env-file "$ENV_FILE_PATH" \
    -v "$BASE_DIR":/app \
    -v "$GOOGLE_CREDENTIALS_PATH":/secrets \
    -p "$APP_PORT_BACKEND":"$APP_PORT_BACKEND" \
    "$IMAGE_NAME" $CMD
